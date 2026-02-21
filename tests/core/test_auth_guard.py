"""Tests for account mismatch guard in profile saving."""

from notebooklm_tools.core.exceptions import AccountMismatchError, NLMError


def test_account_mismatch_error_inherits_nlm_error():
    """AccountMismatchError should be an NLMError."""
    assert issubclass(AccountMismatchError, NLMError)


def test_account_mismatch_error_contains_both_emails():
    """Error message should contain both the stored and new emails."""
    err = AccountMismatchError(
        stored_email="work@company.com",
        new_email="personal@gmail.com",
        profile_name="work",
    )
    assert "work@company.com" in str(err)
    assert "personal@gmail.com" in str(err)
    assert "work" in str(err)


def test_account_mismatch_error_has_hint():
    """Error should include a hint about --force."""
    err = AccountMismatchError(
        stored_email="work@company.com",
        new_email="personal@gmail.com",
        profile_name="work",
    )
    assert "--force" in err.hint
