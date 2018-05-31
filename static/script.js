$(function() {

  $(document).ready(function() {
    $(".container").load("home.html");
});

  $(document).on('click', 'a', function() {

      var url = $(this).attr("data-page");
      //$(".nav li").removeClass("active");
      $(this).addClass("active");
      $('.container').load(url);
  });

  $(".nav li").on("click", function() {
    $(".nav li").removeClass("active");
    $(this).addClass("active");
    $(".container").load($(this).attr("data-page")+".html?r="+makeid());
  });

});

function makeid()
{
    var text = "";
    var possible = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";

    for( var i=0; i < 5; i++ )
        text += possible.charAt(Math.floor(Math.random() * possible.length));

    return text;
}
