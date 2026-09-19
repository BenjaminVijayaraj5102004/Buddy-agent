---
name: sam-cli-agent
description: AWS Serverless and SAM CLI skill for generating template.yaml, running sam init/build/deploy, and managing cloud resources.
---

# SAM CLI Agent Skill

## Tool Usage & Infrastructure
1. **Serverless MCP**: Execute live tools (`sam init`, `sam build`, `sam local invoke`, `sam_deploy`).
2. **File Persistence**: Use `create_text_file` or `patch_text_file_contents` to write `template.yaml` and config to disk.
3. **Standards**: Production-ready YAML with `AWSTemplateFormatVersion: '2010-09-09'` and `Transform: AWS::Serverless-2016-10-31`. Never hardcode secrets.
