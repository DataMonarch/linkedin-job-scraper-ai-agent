# In hello.py or tests
from src.automation.linkedin import LinkedInAutomation


def test_linkedin():
    li_auto = LinkedInAutomation(headless=False)
    page = li_auto.login_and_check()
    li_auto.close()


if __name__ == "__main__":
    test_linkedin()
