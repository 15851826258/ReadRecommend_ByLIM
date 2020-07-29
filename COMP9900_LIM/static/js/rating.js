
$(function () {
    $(".rating-star").mouseover(function (event) {
        event.preventDefault();
        var self = $(this);
        self.prevAll().attr('src', '/static/imgs/rate_light.png');
        self.attr('src', '/static/imgs/rate_light.png')
    });
    $(".rating-star").mouseout(function (event) {
       event.preventDefault();
       var self = $(this);
       self.siblings().attr('src', '/static/imgs/rate_gray.png');
       self.attr('src', '/static/imgs/rate_gray.png')
    });
    $(".rating-star").click(function (event) {
       event.preventDefault();
       var self = $(this);
       var rating_stars = self.prevAll().length;
       var form = $("#rating_form");
       var rating_stars_input = $("input[name='rating_stars']");
       rating_stars_input.val(rating_stars);
       form.submit();
    });
});