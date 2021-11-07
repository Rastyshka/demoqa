package qa.demo.tests;

import com.codeborne.selenide.Configuration;
import org.junit.jupiter.api.BeforeAll;
import qa.demo.pages.RegistrationPage;

public class TestBase {

    RegistrationPage registrationPage = new RegistrationPage();

    @BeforeAll
    static void browserSetting() {
        Configuration.startMaximized = true;
    }

}
