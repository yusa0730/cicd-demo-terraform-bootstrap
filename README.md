# terraform-bootstrap

OIDC Provider と IAM ロールを Terraform で管理するリポジトリです。
全リポジトリの GitHub Actions → AWS 認証基盤を一元管理します。

## このリポジトリの責務

| リポジトリ | 責務 |
|-----------|------|
| `terraform-bootstrap`（このリポジトリ） | OIDC Provider・IAM ロール（CI/CD 認証基盤） |
| `terraform-accounts` | GuardDuty・CloudTrail・Config・IAM Password Policy 等のアカウントセキュリティ基盤 |
| `terraform-repo` | VPC・ECS・RDS・ALB・ECR 等のアプリ実行基盤 |
| `app-repo` | アプリケーションコード・ECS デプロイ |

### なぜ分離するか

`terraform-repo` や `terraform-accounts` の CI/CD が使う IAM ロールを、それらのリポジトリ自身が変更できてしまうのは権限境界として問題です。
bootstrap を独立したリポジトリにすることで、**IAM ロールの変更には terraform-bootstrap への PR レビューと CODEOWNERS 承認が必要** になります。

## 管理リソース

各環境（dev / stg / prod）の AWS アカウントに以下を作成します。

| リソース | 用途 |
|---------|------|
| `aws_iam_openid_connect_provider` | GitHub Actions OIDC 認証基盤 |
| `*-terraform-plan-role` | terraform-repo の PR plan 用ロール |
| `*-terraform-apply-role` | terraform-repo の apply 用ロール |
| `*-app-deploy-role` | app-repo の ECS デプロイ用ロール |
| `*-accounts-plan-role` | terraform-accounts の PR plan 用ロール |
| `*-accounts-apply-role` | terraform-accounts の apply 用ロール |

---

## はじめに（初回セットアップ）

### 前提条件

- AWS アカウントへの AdministratorAccess を持つ IAM ユーザーが作成済みであること
- GitHub リポジトリが作成済みであること

---

### Step 1: 一時的な bootstrap 用 IAM ユーザーを作成する

AWS Console の各アカウントで以下を実行します。

```
IAM → Users → Create user
  User name: bootstrap-user（任意）
  Permissions: AdministratorAccess（アタッチ）
  Access key: Create access key → Application running outside AWS
```

> [!IMPORTANT]
> この IAM ユーザーと Access Key は bootstrap 完了後に必ず削除します。

---

### Step 2: GitHub に Environments を登録する

`Settings → Environments` で `bootstrap-dev` / `bootstrap-stg` / `bootstrap-prod` を作成します。

各 Environment に以下の Secrets を登録します。

| Secret 名 | 値 |
|-----------|---|
| `AWS_BOOTSTRAP_ACCESS_KEY_ID` | Step 1 で作成した Access Key ID |
| `AWS_BOOTSTRAP_SECRET_ACCESS_KEY` | Step 1 で作成した Secret Access Key |

`bootstrap-prod` Environment には Required reviewers を設定することを推奨します。

---

### Step 3: CODEOWNERS を設定する

`.github/CODEOWNERS` の `@your-org/infra-approvers` を実際の Team 名に変更します。

---

### Step 4: Branch Protection Rules を設定する

`Settings → Branches → Add branch ruleset` で `main` ブランチを設定します。

| 項目 | 値 |
|-----|---|
| Require a pull request before merging | ✅ |
| Require approvals | ✅（1 以上） |
| Require review from Code Owners | ✅ |
| Require status checks to pass | ✅ |
| Required status checks | `bootstrap-fmt` |

---

### Step 5: bootstrap を実行する

`Actions → bootstrap → Run workflow` を開き、以下を選択します。

| 入力 | 値 |
|-----|---|
| Target environment | `dev`（最初に実行する環境） |
| Action | `plan` |

**plan の内容を確認したら、`apply` で再実行します。**

| 入力 | 値 |
|-----|---|
| Target environment | `dev` |
| Action | `apply` |

stg / prod も同様に実行します（dev から推奨、独立して実行可能）。

---

### Step 6: 出力 ARN を各リポジトリの Secrets に登録する

apply 完了後の Step Summary に表示された ARN を以下に登録します。

#### terraform-repo の Repository Secrets

| Secret 名 | 値 |
|-----------|---|
| `AWS_TERRAFORM_PLAN_ROLE_ARN_DEV` | Step Summary の `terraform_plan_role_arn`（dev） |
| `AWS_TERRAFORM_PLAN_ROLE_ARN_STG` | Step Summary の `terraform_plan_role_arn`（stg） |
| `AWS_TERRAFORM_PLAN_ROLE_ARN_PROD` | Step Summary の `terraform_plan_role_arn`（prod） |

#### terraform-repo の GitHub Environments

| Environment | Secret 名 | 値 |
|------------|-----------|---|
| `dev` | `AWS_TERRAFORM_ROLE_ARN` | Step Summary の `terraform_apply_role_arn`（dev） |
| `stg` | `AWS_TERRAFORM_ROLE_ARN` | Step Summary の `terraform_apply_role_arn`（stg） |
| `prod` | `AWS_TERRAFORM_ROLE_ARN` | Step Summary の `terraform_apply_role_arn`（prod） |

#### app-repo の GitHub Environments

| Environment | Secret 名 | 値 |
|------------|-----------|---|
| `dev` | `AWS_DEPLOY_ROLE_ARN` | Step Summary の `app_deploy_role_arn`（dev） |
| `stg` | `AWS_DEPLOY_ROLE_ARN` | Step Summary の `app_deploy_role_arn`（stg） |
| `prod` | `AWS_DEPLOY_ROLE_ARN` | Step Summary の `app_deploy_role_arn`（prod） |

#### terraform-accounts の Repository Secrets

| Secret 名 | 値 |
|-----------|---|
| `AWS_ACCOUNTS_PLAN_ROLE_ARN_DEV` | Step Summary の `accounts_plan_role_arn`（dev） |
| `AWS_ACCOUNTS_PLAN_ROLE_ARN_STG` | Step Summary の `accounts_plan_role_arn`（stg） |
| `AWS_ACCOUNTS_PLAN_ROLE_ARN_PROD` | Step Summary の `accounts_plan_role_arn`（prod） |

#### terraform-accounts の GitHub Environments

| Environment | Secret 名 | 値 |
|------------|-----------|---|
| `dev` | `AWS_ACCOUNTS_ROLE_ARN` | Step Summary の `accounts_apply_role_arn`（dev） |
| `stg` | `AWS_ACCOUNTS_ROLE_ARN` | Step Summary の `accounts_apply_role_arn`（stg） |
| `prod` | `AWS_ACCOUNTS_ROLE_ARN` | Step Summary の `accounts_apply_role_arn`（prod） |

---

### Step 7: bootstrap 用 IAM ユーザーを削除する

> [!WARNING]
> この手順を必ず実施してください。長期運用 IAM 認証情報を残すことはセキュリティリスクです。

```
1. GitHub Environment bootstrap-<env> から AWS_BOOTSTRAP_ACCESS_KEY_ID を削除
2. GitHub Environment bootstrap-<env> から AWS_BOOTSTRAP_SECRET_ACCESS_KEY を削除
3. AWS Console → IAM → Users → bootstrap-user を削除
```

---

## bootstrap 変更時の運用フロー

IAM ロールのポリシー変更などが必要な場合は、PR を通じて管理します。

```
1. feature ブランチを作成して main へ PR を出す
   → bootstrap-fmt が自動実行される（フォーマットチェック）
   → CODEOWNERS (infra-approvers) が内容を review する

2. PR がマージされたら、Actions → bootstrap → Run workflow で apply を実行する
   → action=plan で変更内容を確認
   → action=apply で適用
```

> `workflow_dispatch` で実行するため、PR マージ後の apply は手動トリガーです。
> IAM ロール変更は影響範囲が広いため、意図的に自動 apply としていません。

---

## ディレクトリ構成

```
environments/
├── dev/    dev アカウントの OIDC Provider + IAM ロール
├── stg/    stg アカウントの OIDC Provider + IAM ロール
└── prod/   prod アカウントの OIDC Provider + IAM ロール
```

各環境は独立した S3 バックエンドで状態管理されます。

---

## ドキュメント

| ドキュメント | 内容 |
|------------|------|
| [アーキテクチャ](../terraform-repo/docs/architecture.md) | AWS 構成・ネットワーク・ECS・RDS・IAM の詳細 |
| [CI/CD](../terraform-repo/docs/cicd.md) | Workflows 一覧・Secrets 一覧 |
