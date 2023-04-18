#!/usr/bin/env python3
"""
Helper to facilitate conversion of other tools checks
"""

from dataclasses import dataclass
import json
import logging
import os
from pathlib import Path
import shutil

import click
from ruamel.yaml import YAML


log = logging.getLogger("pgen")


KICS_PREFIX_SERVICE_MAP = {
    "user_with": "iam",
    "user_data": "ec2",
    "vulnerable": "acm",
    "role": "iam",
    "resource": "resource",
    "authentication": "iam",
    "ca": "acm",
    "certificate": "acm",
    "cdn": "cloudfront",
    "db": "rds",
    "group": "iam",
    "http": "security-group",
    "instance": "ec2",
    "remote": "security-group",
    "security_group": "security-group",
    "sensitive_port": "security-group",
    "stack": "cfn",
    "unknown": "security-group",
    "unrestricted": "security-group",
    "aws_password": "iam",
}


@dataclass
class PolicyTransform:

    name: str
    description: str
    severity: str
    category: str
    provider: str
    id: str
    path: Path
    source: str
    source_path: str
    service: str
    root_source: Path

    def as_dict(self):
        return {
            "name": self.name,
            "description": self.description,
            "resource": f"terraform.{self.provider}_{self.service}*",
            "metadata": {
                "severity": self.severity,
                "category": self.category,
                "provider": self.provider,
                "source": self.source,
                "source_path": str(self.relative_path),
            },
        }


class KicsPolicyTransform(PolicyTransform):

    rule_path = "assets" + os.sep + "queries"

    @staticmethod
    def get_policy_name(rule_dir):
        return rule_dir.name.replace("_", "-")

    @classmethod
    def from_source(cls, rule_dir, root_source):
        service = cls.resolve_service(rule_dir)
        policy_name = cls.get_policy_name(rule_dir)
        if not policy_name.startswith(service):
            policy_name = f"{service}-{policy_name}"
        md = cls.extract_metadata(rule_dir)
        md.pop("name")
        return cls(
            name=policy_name,
            source="kics",
            source_path=rule_dir,
            service=service,
            root_source=root_source,
            **md,
        )

    @classmethod
    def extract_metadata(self, rule_dir: Path):
        check = json.loads((rule_dir / "metadata.json").read_text())
        return dict(
            id=check["id"],
            provider=check["cloudProvider"],
            severity=check["severity"].title(),
            description=check["descriptionText"],
            name=rule_dir.parent.name,
            category=check["category"],
            path=rule_dir,
        )

    @property
    def relative_path(self):
        return self.source_path.relative_to(
            self.root_source.parent.parent.parent.parent
        )

    @property
    def count_test_cases(self):
        return len(list((self.source_path / "test").rglob("*.tf")))

    def copy_source(self, policy_dir):
        source_dir = policy_dir / "source"
        source_dir.mkdir(exist_ok=True)
        source_copy_dest = source_dir / (self.name + ".rego")
        shutil.copyfile(self.path / "query.rego", source_copy_dest)

    def copy_tests(self, policy_dir):
        policy_test_dir = policy_dir / "tests" / self.name

        def ignore(src, names):
            return ["left.plan.yaml"]

        shutil.copytree(
            self.source_path / "test",
            policy_test_dir,
            ignore=ignore,
            dirs_exist_ok=True,
        )
        source_test_plan_path = policy_test_dir / "positive_expected_result.json"
        source_test_plan = json.loads(source_test_plan_path.read_text())
        os.remove(source_test_plan_path)
        target_test_plan_path = policy_test_dir / "left.plan.yaml"

        with open(target_test_plan_path, "w") as fh:
            YAML().dump(
                [
                    {
                        "resource.__tfmeta.filename": case.get(
                            "fileName", "positive.tf"
                        ),
                        "file_line_start": case.get("line", 1),
                    }
                    for case in source_test_plan
                ],
                stream=fh,
            )

    @classmethod
    def discover_rules(cls, rules_dir, rules_prefix):
        return rules_dir.rglob(rules_prefix)

    @staticmethod
    def resolve_service(rule_dir):
        candidate = rule_dir.name.split("_", 1)[0]
        return KICS_PREFIX_SERVICE_MAP.get(candidate, candidate)

    @classmethod
    def resolve_policy_file(cls, policy_dir, rule_dir):
        return policy_dir / (cls.resolve_service(rule_dir) + ".yaml")


class PolicyCollection:
    def __init__(self, policy_file: Path, policies=()):
        self.policies = policies
        self.policy_file = policy_file

    def save(self):
        if self.policy_file.exists():
            self.update_file()
        else:
            self.create_file()
        for p in self.policies:
            p.copy_tests(self.policy_file.parent)
            p.copy_source(self.policy_file.parent)

    def create_file(self):
        with open(self.policy_file, "w") as fh:
            yaml = YAML()
            yaml.representer.ignore_aliases = lambda *data: True
            yaml.dump({"policies": [p.as_dict() for p in self.policies]}, stream=fh)

    def update_file(self):
        pmap = {p.name: p for p in self.policies}
        extant = YAML().load(self.policy_file.read_text())
        if not extant:
            return self.create_file()

        extant_map = {
            p["name"]: idx for idx, p in enumerate(extant.get("policies", ()))
        }
        for pname in pmap:
            if pname in extant_map:
                extant["policies"][extant_map[pname]] = self.update_policy_metadata(
                    pmap[pname], extant["policies"][extant_map[pname]]
                )
            else:
                extant["policies"].append(pmap[pname].as_dict())
        with open(self.policy_file, "w") as fh:
            yaml = YAML()
            yaml.representer.ignore_aliases = lambda *data: True
            yaml.dump(extant, stream=fh)

    def update_policy_metadata(self, source, target):
        return target


SOURCE_TYPE = {"kics": KicsPolicyTransform}


@click.command()
@click.option("-r", "--rule-prefix", required=True)
@click.option("-s", "--source-dir", required=True, type=Path)
@click.option("--skip", multiple=True)
@click.option("-p", "--policy-dir", required=True, type=Path)
@click.option("-t", "--source-type", default="kics")
@click.option("--language", default="terraform")
@click.option("--provider", default="aws")
@click.option("--check", default=False, is_flag=True)
def main(
    rule_prefix, provider, check, source_dir, policy_dir, source_type, language, skip
):
    logging.basicConfig(level=logging.DEBUG)
    source_class = SOURCE_TYPE[source_type]
    rules_dir = source_dir.expanduser() / source_class.rule_path / language / provider
    policy_dir = Path(policy_dir).expanduser() / provider
    policy_map = {}

    if not rule_prefix.endswith("*"):
        rule_prefix += "*"

    log.info(f"Copying {source_type}:{language}:{provider}")
    for source_path in source_class.discover_rules(rules_dir, rule_prefix):
        if source_path.name in skip:
            continue
        policy_file = source_class.resolve_policy_file(policy_dir, source_path)
        policy = source_class.from_source(source_path, rules_dir)
        if check:
            log.info(
                f"Copying {policy.relative_path} to {policy_file} [{policy.name}] w/ {policy.count_test_cases} tests"
            )
            continue
        policy_map.setdefault(policy_file, []).append(policy)

    for policy_file, policies in policy_map.items():
        test_count = sum([p.count_test_cases for p in policies])
        log.info(
            f"Writing out {policy_file} w/ {len(policies)} policies w/ {test_count} test cases"
        )
        PolicyCollection(policy_file, policies).save()


if __name__ == "__main__":
    try:
        main()
    except Exception:
        import traceback, sys, pdb

        traceback.print_exc()
        pdb.post_mortem(sys.exc_info()[-1])
