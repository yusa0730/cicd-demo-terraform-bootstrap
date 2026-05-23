# cicd-demo-terraform-bootstrap

このリポジトリは GitHub Actions が AWS に入るための権限基盤を管理する Terraform repository。

## 責務

**このrepoで管理する:**
- GitHub OIDC Provider（AWS と GitHub を繋ぐ信頼基盤）
- Terraform plan IAM Role（各環境）
- Terraform apply IAM Role（各環境）
- App deploy IAM Role（各環境）
- 上記 Role の IAM trust policy（OIDC sub 条件）

**このrepoで管理しない:**
- VPC / ECS / RDS / ALB などのアプリケーション基盤
- AWS account baseline（GuardDuty / CloudTrail / Config / Security Hub）
- アプリケーション SSM Parameter / Secrets Manager

上記は別repoで管理する:
- `cicd-demo-terraform` → アプリ基盤
- `cicd-demo-terraform-accounts` → account baseline

## 最重要ルール

**bootstrap repo は権限境界である。**

- 他 repo が自分自身の apply role を変更できる設計にしない
- trust policy の OIDC `sub` 条件は必ず workflow trigger と照合する
- Role ARN は他 repo の GitHub Secrets に登録する（Terraform で直接渡さない）

## OIDC sub 条件の照合ルール

`sub` 条件と workflow の `on:` trigger が必ず一致していること:

| trigger | 正しいsub条件 |
|---|---|
| `pull_request` | `repo:org/repo:pull_request` |
| `push` to branch | `repo:org/repo:ref:refs/heads/<branch>` |
| `workflow_dispatch` | `repo:org/repo:ref:refs/heads/<branch>` |
| environment | `repo:org/repo:environment:<env>` |

## 変更時に必ず確認すること

1. trust policy の `sub` 条件と実際の workflow trigger を照合する
2. plan Role と apply Role が分離されているか確認する
3. 他 repo の GitHub Secrets / Environment Secrets と Role ARN が一致しているか確認する
4. destroy 後も OIDC Provider は残ること（他 repo が依存）

## 禁止事項

- OIDC Provider を `terraform destroy` で削除させない（他 repo 全体が壊れる）
- apply Role に `AdministratorAccess` を付与しない
- trust policy の条件なし（`*`）での発行を許可しない
- このセッション内で `terraform apply` / `terraform destroy` を直接実行しない
