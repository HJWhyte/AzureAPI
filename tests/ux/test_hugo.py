"""Hugo test suite"""
# pylint: disable=no-member
import pytest
from selenium.webdriver.support.ui import WebDriverWait  # pylint: disable=import-error  # noqa: E501
from selenium.webdriver.common.by import By  # pylint: disable=import-error

DEFAULT_TIMEOUT = 15
SITENAME = "Welcome to the Phoenix Project!"


def get_default_url(url):
    """get the default URL for the site"""
    if url[-1] == "/":  # pylint: disable=no-else-return
        return url
    else:
        return url + "/"


def get_default_title():
    """Get the default title of the site"""
    return SITENAME


@pytest.mark.usefixtures("setup")
class TestHugo:
    """Class to analyse the web site"""
    def get_button_by_link_name(self, linktext):
        """get button from a specific link"""
        return self.driver.find_element(By.LINK_TEXT, linktext)

    def wait_for_page_to_load(self, url, title):
        """wait for a page to load"""
        self.driver.get(url)
        WebDriverWait(self.driver, DEFAULT_TIMEOUT).until(
            lambda driver: title in self.driver.title
        )

    def load_index_page(self, url):
        """Load the index page"""
        self.wait_for_page_to_load(url, get_default_title())

    def test_index_page(self, url):
        """check the index page is configured correctly"""
        page_url = get_default_url(url)
        page_title = "Welcome to the Phoenix Project! | Welcome to the Phoenix Project!"  # pylint: disable=line-too-long  # noqa: E501

        self.load_index_page(url)
        assert page_title == self.driver.title
        assert page_url == self.driver.current_url
        self.driver.save_screenshot("test_index_page_00.png")

    def test_change1_post(self, url):
        """check the change1 post is configured correctly"""
        self.load_index_page(url)

        page_url = get_default_url(url)+"posts/git_init/"
        page_title = "Change_1 | "+get_default_title()

        change1_post = self.get_button_by_link_name("Change_1")
        change1_post.click()

        self.wait_for_page_to_load(page_url, page_title)

        assert page_title == self.driver.title
        assert page_url == self.driver.current_url

        self.driver.save_screenshot("test_first_post_00.png")

    def test_second_post(self, url):
        """check the second post is configured correctly"""
        self.load_index_page(url)

        page_url = get_default_url(url)+"posts/raci/"
        page_title = "Colleague Introduction and RACI | "+get_default_title()

        second_post = self.get_button_by_link_name("Colleague Introduction and RACI")  # noqa: E501
        second_post.click()

        self.wait_for_page_to_load(page_url, page_title)

        assert page_title == self.driver.title
        assert page_url == self.driver.current_url

        self.driver.save_screenshot("test_second_post_00.png")

    def test_third_post(self, url):
        """check the third post is configured correctly"""
        self.load_index_page(url)

        page_url = get_default_url(url)+"posts/post_mortem/"
        page_title = "The Phoenix Project - Postmortem | "+get_default_title()

        third_post = self.get_button_by_link_name("The Phoenix Project - Postmortem")  # noqa: E501
        third_post.click()

        self.wait_for_page_to_load(page_url, page_title)

        assert page_title == self.driver.title
        assert page_url == self.driver.current_url

        self.driver.save_screenshot("test_third_post_00.png")

    def test_change2_post(self, url):
        """check the change2 post is configured correctly"""
        self.load_index_page(url)

        page_url = get_default_url(url)+"posts/git_clone_2/"
        page_title = "Change_2 | "+get_default_title()

        change2_post = self.get_button_by_link_name("Change_2")  # noqa: E501
        change2_post.click()

        self.wait_for_page_to_load(page_url, page_title)

        assert page_title == self.driver.title
        assert page_url == self.driver.current_url

        self.driver.save_screenshot("test_change2_post_00.png")

    def test_change3_post(self, url):
        """check the change3 post is configured correctly"""
        self.load_index_page(url)

        page_url = get_default_url(url)+"posts/git_branch_3/"
        page_title = "Change_3 | "+get_default_title()

        change3_post = self.get_button_by_link_name("Change_3")  # noqa: E501
        change3_post.click()

        self.wait_for_page_to_load(page_url, page_title)

        assert page_title == self.driver.title
        assert page_url == self.driver.current_url

        self.driver.save_screenshot("test_change3_post_00.png")

    def test_change4_post(self, url):
        """check the change4 post is configured correctly"""
        self.load_index_page(url)

        page_url = get_default_url(url)+"posts/git_add_4/"
        page_title = "Change_4 | "+get_default_title()

        change4_post = self.get_button_by_link_name("Change_4")  # noqa: E501
        change4_post.click()

        self.wait_for_page_to_load(page_url, page_title)

        assert page_title == self.driver.title
        assert page_url == self.driver.current_url

        self.driver.save_screenshot("test_change4_post_00.png")

    def test_change5_post(self, url):
        """check the change5 post is configured correctly"""
        self.load_index_page(url)

        page_url = get_default_url(url)+"posts/git_commit_5/"
        page_title = "Change_5 | "+get_default_title()

        change5_post = self.get_button_by_link_name("Change_5")  # noqa: E501
        change5_post.click()

        self.wait_for_page_to_load(page_url, page_title)

        assert page_title == self.driver.title
        assert page_url == self.driver.current_url

        self.driver.save_screenshot("test_change5_post_00.png")

    def test_change6_post(self, url):
        """check the change6 post is configured correctly"""
        self.load_index_page(url)

        page_url = get_default_url(url)+"posts/git_push_6/"
        page_title = "Change_6 | "+get_default_title()

        change6_post = self.get_button_by_link_name("Change_6")  # noqa: E501
        change6_post.click()

        self.wait_for_page_to_load(page_url, page_title)

        assert page_title == self.driver.title
        assert page_url == self.driver.current_url

        self.driver.save_screenshot("test_change6_post_00.png")

    def test_change7_post(self, url):
        """check the change7 post is configured correctly"""
        self.load_index_page(url)

        page_url = get_default_url(url)+"posts/git_pull_7/"
        page_title = "Change_7 | "+get_default_title()

        change6_post = self.get_button_by_link_name("Change_7")  # noqa: E501
        change6_post.click()

        self.wait_for_page_to_load(page_url, page_title)

        assert page_title == self.driver.title
        assert page_url == self.driver.current_url

        self.driver.save_screenshot("test_change7_post_00.png")
