package qa.demo;

import com.codeborne.selenide.Configuration;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;


import java.io.File;


import static com.codeborne.selenide.Condition.text;
import static com.codeborne.selenide.Selectors.byText;
import static com.codeborne.selenide.Selenide.*;


public class ValidationTests {

    @BeforeAll
    static void browserSetting(){

        Configuration.startMaximized = true;
    }

    @Test
    void fillFormTest(){
        //open browser
        open("https://demoqa.com/automation-practice-form");

        //fill first name
        $("#firstName").setValue("Some first name");

        //fill last name
        $("#lastName").setValue("Some last name");

        //fill email
        $("#userEmail").setValue("sample@gmail.com");

        //choose gender
        $(".custom-control-label").click();

        //fill number
        $("#userNumber").setValue("7777777777");

        // choose date of birth
        $("#dateOfBirthInput").click();
        $(".react-datepicker__month-select").selectOptionByValue("2");
        $(".react-datepicker__year-select").selectOptionByValue("1996");
        $$(".react-datepicker__day").find(text("20")).click();

        //choose subjects
        $("#subjectsInput").click();
        $("#subjectsInput").setValue("M");
        $(byText("Maths")).click();

        //choose hobbies
        $("[for='hobbies-checkbox-1']").click();

        //upload image
        File img = new File("src/test/resources/img.png");
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
        $(".table-responsive").find(byText("Student Name")).parent().shouldHave(text("Some first name Some last name"));
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
