output "terraform_plan_role_arn" {
  description = "Set as AWS_TERRAFORM_PLAN_ROLE_ARN_DEV in terraform-repo Repository Secrets"
  value       = aws_iam_role.terraform_plan.arn
}

output "terraform_apply_role_arn" {
  description = "Set as AWS_TERRAFORM_ROLE_ARN in terraform-repo GitHub Environment dev"
  value       = aws_iam_role.terraform_apply.arn
}

output "app_deploy_role_arn" {
  description = "Set as AWS_DEPLOY_ROLE_ARN in app-repo GitHub Environment dev"
  value       = aws_iam_role.app_deploy.arn
}

output "accounts_plan_role_arn" {
  description = "Set as AWS_ACCOUNTS_PLAN_ROLE_ARN_DEV in terraform-accounts Repository Secrets"
  value       = aws_iam_role.accounts_plan.arn
}

output "accounts_apply_role_arn" {
  description = "Set as AWS_ACCOUNTS_ROLE_ARN in terraform-accounts GitHub Environment dev"
  value       = aws_iam_role.accounts_apply.arn
}
