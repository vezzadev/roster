# Gate verification

Temporary file to test the `pr-review-gate` environment + `required_deployments`
ruleset rule end-to-end. The PR opened from this branch should:

1. Run the `Human review gate` workflow.
2. Pause at "Awaiting human review" with state `waiting` until a configured
   reviewer (`pedropaulovc` or `pedrovezzadev`) clicks **Review deployments →
   Approve and deploy**.
3. Unblock merge only after the deployment succeeds.

Delete this file once verified.
