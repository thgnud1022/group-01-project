# QA FINDINGS

## QF-001 — PO can be created before PR approval

### Source
Kiro Verify Audit — V-03

### Related Requirement
REQ-BR-10

### Severity
CRITICAL

### Description
The current create PO flow does not verify that
the Purchase Request has status APPROVED before
creating the Purchase Order.

### Expected
PO creation must be rejected when PR is not APPROVED.

### Actual
create_po() only verifies that the PR exists.

### Status
OPEN

### Verification
Verified directly against source code.

### Evidence
Kiro Verify Audit — V-03