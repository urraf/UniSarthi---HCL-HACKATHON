"""Accounts: sign up with OTP, login, forgot password, staff login (in-memory MongoDB, OTP emails printed)."""
import pytest

from app import auth
from app.account_routes import (EmailOnly, Login, ResetPassword, SignupStart, SignupVerify, forgot_password,
                                login, reset_password, signup_start, signup_verify)
from app.mongo import get_db


@pytest.fixture
def codes(monkeypatch):
    """Capture the OTPs instead of emailing them."""
    sent = []
    real = auth.create_otp

    def capture(*args, **kwargs):
        code = real(*args, **kwargs)
        sent.append(code)
        return code

    monkeypatch.setattr(auth, "create_otp", capture)
    return sent


def test_signup_login_and_reset(codes):
    signup_start(SignupStart(roll_number="2024ucs0001", email="test.exact@nsut.ac.in"))
    signup_verify(SignupVerify(email="test.exact@nsut.ac.in", otp=codes[-1], password="first-pass-1"))
    assert login(Login(roll_number="2024UCS0001", password="first-pass-1"))["student_id"] == "S0001"

    forgot_password(EmailOnly(email="test.exact@nsut.ac.in"))
    reset_password(ResetPassword(email="test.exact@nsut.ac.in", otp=codes[-1], new_password="second-pass-2"))
    assert login(Login(roll_number="2024UCS0001", password="second-pass-2"))["token"]


def test_only_university_email_allowed():
    with pytest.raises(Exception):
        signup_start(SignupStart(roll_number="2024UCS0002", email="someone@gmail.com"))


def test_wrong_otp_is_rejected(codes):
    signup_start(SignupStart(roll_number="2024UCS0002", email="test.below@nsut.ac.in"))
    with pytest.raises(Exception):
        signup_verify(SignupVerify(email="test.below@nsut.ac.in", otp="000000" if codes[-1] != "000000" else "111111",
                                   password="some-pass-1"))


def test_staff_token_is_not_a_student_token():
    auth.create_admin("staff.test", "staff-pass-1")
    role, subject = auth.verify_token(auth.admin_login("staff.test", "staff-pass-1"))
    assert (role, subject) == ("admin", "staff.test")
    assert get_db().admins.count_documents({"admin_id": "staff.test"}) == 1
