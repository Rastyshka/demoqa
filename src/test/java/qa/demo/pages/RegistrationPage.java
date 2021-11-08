package qa.demo.pages;

import com.codeborne.selenide.SelenideElement;
import qa.demo.pages.components.CalendarComponent;

import java.io.File;

import static com.codeborne.selenide.Condition.text;
import static com.codeborne.selenide.Selectors.byText;
import static com.codeborne.selenide.Selenide.$;
import static com.codeborne.selenide.Selenide.open;

public class RegistrationPage {

    private SelenideElement resultsTable = $(".table-responsive");

    public RegistrationPage openPage() {
        //open browser
        open("https://demoqa.com/automation-practice-form");
        return this;
    }

    public RegistrationPage typeFirstName(String firstName) {
        $("#firstName").setValue(firstName);
        return this;
    }

    public RegistrationPage typeLastName(String lastName) {
        $("#lastName").setValue(lastName);
        return this;
    }

    public RegistrationPage typeEmail(String userEmail) {
        $("#userEmail").setValue(userEmail);
        return this;
    }

    public RegistrationPage chooseGender() {
        $("[for='gender-radio-1']").click();
        return this;
    }

    public RegistrationPage typeNumber(String userNumber) {
        $("#userNumber").setValue(userNumber);
        return this;
    }

    public RegistrationPage setDate(String day, String month, String year) {
        new CalendarComponent().setDate(day, month, year);
        return this;
    }

    public RegistrationPage typeSubject(String key, String subject) {
        $("#subjectsInput").click();
        $("#subjectsInput").sendKeys(key);
        $(byText(subject)).click();
        return this;
    }

    public RegistrationPage chooseHobbies(String hobby) {
        $(byText(hobby)).click();
        return this;
    }

    public RegistrationPage uploadImage(String path) {
        File img = new File(path);
        $("#uploadPicture").uploadFile(img);
        return this;
    }

    public RegistrationPage typeAddress(String address) {
        $("#currentAddress").setValue(address);
        return this;
    }

    public RegistrationPage chooseState(String state) {
        $("#state").scrollTo().click();
        $("#state").find(byText(state)).click();
        return this;
    }

    public RegistrationPage chooseCity(String city) {
        $("#city").scrollTo().click();
        $("#city").find(byText(city)).click();
        return this;
    }

    public void submit() {
        $("#submit").click();
    }

    public RegistrationPage checkResultsValue(String key, String value) {
        resultsTable.$(byText(key))
                .sibling(0).shouldHave(text(value));
        return this;
    }


}
