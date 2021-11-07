package qa.demo.tests;

import com.github.javafaker.Faker;
import org.junit.jupiter.api.Test;

import java.io.File;
import java.util.Locale;

import static com.codeborne.selenide.Condition.text;
import static com.codeborne.selenide.Selectors.byText;
import static com.codeborne.selenide.Selenide.$;
import static com.codeborne.selenide.Selenide.$$;


public class ValidationTests extends TestBase {

    Faker faker = new Faker(new Locale("ru"));

    String firstName = faker.name().firstName(),
            lastName = faker.name().lastName(),
            email = faker.internet().emailAddress(),
            phoneNumber = faker.phoneNumber().subscriberNumber(10),
            address = faker.address().fullAddress(),
            state = "Haryana",
            city = "Karnal";

    @Test
    void fillFormTest() {

        //open page
        registrationPage.openPage()
                .typeFirstName(firstName)
                .typeLastName(lastName)
                .typeEmail(email)
                .chooseGender("Male")
                .typeNumber(phoneNumber)
                .setDate("20", "March", "1996")
                .typeSubject("M", "Math")
                        .
                














        //choose hobbies
        $("[for='hobbies-checkbox-1']").click();

        //upload image
        File img = new File("src/test/resources/img/img.png");
        $("#uploadPicture").uploadFile(img);

        //fill adress
        $("#currentAddress").setValue("some adress");

        //Choose state
        $("#state").scrollTo().click();
        $("#state").find(byText("Haryana")).click();

        //Choose city
        $("#city").click();
        $("#city").find(byText("Karnal")).click();

        //press to Submit button
        $("#submit").click();

        //check fill data
        $(".table-responsive tr:nth-child(1) td:nth-child(2)").shouldHave(text("Some first name Some last name"));
        $(".table-responsive").find(byText("Student Email")).parent().shouldHave(text("sample@gmail.com"));
        $(".table-responsive").find(byText("Gender")).parent().shouldHave(text("Male"));
        $(".table-responsive").find(byText("Mobile")).parent().shouldHave(text("7777777777"));
        $(".table-responsive").find(byText("Date of Birth")).parent().shouldHave(text("20 March,1996"));
        $(".table-responsive").find(byText("Subjects")).parent().shouldHave(text("Maths"));
        $(".table-responsive").find(byText("Hobbies")).parent().shouldHave(text("Sports"));
        $(".table-responsive").find(byText("Picture")).parent().shouldHave(text("img.png"));
        $(".table-responsive").find(byText("Address")).parent().shouldHave(text("some adress"));
        $(".table-responsive").find(byText("State and City")).parent().shouldHave(text("Haryana Karnal"));

    }

}
