package qa.demo.pages;

import qa.demo.pages.components.CalendarComponent;

import static com.codeborne.selenide.Selectors.byText;
import static com.codeborne.selenide.Selenide.$;
import static com.codeborne.selenide.Selenide.open;

public class RegistrationPage {

    public RegistrationPage openPage() {
        //open browser
        open("https://demoqa.com/automation-practice-form");
        return this;
    }

     public RegistrationPage typeFirstName(String firstName){
         $("#firstName").setValue(firstName);
         return this;
     }

    public RegistrationPage typeLastName(String lastName){
        $("#lastName").setValue(lastName);
        return this;
    }
    public RegistrationPage typeEmail(String userEmail){
        $("#userEmail").setValue(userEmail);
        return this;
    }

    public RegistrationPage chooseGender(String gender) {
        $(".custom-control-label").find(byText(gender)).click();
        return this;
    }

    public RegistrationPage typeNumber(String userNumber){
        $("#userEmail").setValue(userNumber);
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

    public RegistrationPage chooseHobbies






}
