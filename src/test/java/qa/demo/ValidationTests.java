package qa.demo;

import org.junit.jupiter.api.Test;


import static com.codeborne.selenide.Condition.text;
import static com.codeborne.selenide.Selenide.*;


public class ValidationTests {
    @Test
    void fillFormTest(){
        open("https://demoqa.com/automation-practice-form");
        $("#firstName").setValue("Some first name");
        $("#lastName").setValue("Some last name");
        $("#userEmail").setValue("sample@gmail.com");
        $(".custom-control-label").click();
        $("#userNumber").setValue("7777777777");
        $("#dateOfBirthInput").click();
        $(".react-datepicker__month-select").selectOptionByValue("2");
        $(".react-datepicker__year-select").selectOptionByValue("1996");
        $$(".react-datepicker__day").find(text("20")).click();
      //  $(".subjects-auto-complete__control").click();
       // $(".subjects-auto-complete__control--is-focused").setValue("Maths").pressEnter();
        $("title.hobbies-checkbox-1").click();







    }

}
