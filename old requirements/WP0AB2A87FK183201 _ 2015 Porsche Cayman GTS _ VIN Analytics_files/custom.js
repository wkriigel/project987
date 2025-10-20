let $body = $('body'),
    $siteHeader = $('.site-header'),
    menuOffset = $siteHeader.offset().top,
    scrollFromTop = $(window).scrollTop();


$(window).on('load', function () {
	if( /Android|webOS|iPhone|iPad|iPod|BlackBerry/i.test(navigator.userAgent) ) $body.addClass('ios');
	else $body.addClass('web');
});


/* ==========================================================================
   When the window is scrolled, do
   ========================================================================== */
   
	$(window).scroll(function() {

    if ( $(window).scrollTop() > 0 ) $siteHeader.addClass('fixed');
    else $siteHeader.removeClass('fixed');
		
	});

/* ==========================================================================
   When the window is resized, do
   ========================================================================== */
   
	$(window).resize(function() {

    setEqualHeight('.pie-charts-container .canvas-container');
		
	});



$(function(){

  if ( scrollFromTop > 0 ) $siteHeader.addClass('fixed');

  $('.close').on('click', function(){
    $(this).parent().fadeOut();
  });


  $('.menu-toggle').on('click', function(){
    $(this).toggleClass('active');
    $('.header-nav .main-menu').slideToggle();
  });

  $('.mob-menu-toggle').on('click', function(){
    $(this).toggleClass('show-menu');
    $(this).next('ul').children('li:not(.active)').slideToggle();
  });

  $('.deepview-nav .has-children').on('click', function(){
    $(this).find('.sub-menu').slideToggle();
  });

  $('table.has-details').each(function() {
    $(this).find('tr:odd').addClass('odd');
  });

  $('.details-control').on('click', function(){
    $(this).parent().next('.details').slideToggle();
  });


  $('.section-contact textarea').each(function () {
    this.setAttribute('style', 'height:' + (this.scrollHeight) + 'px;overflow-y:hidden;');
  }).on('input', function () {
    this.style.height = 'auto'; //this.style.height = 0;
    this.style.height = (this.scrollHeight) + 'px';
  });

  setEqualHeight('.pie-charts-container .canvas-container');

});

function setEqualHeight(element) {
  $(element).each(function(){
    let el = $(this);
    el.css({'height':el.width()+'px'});
  });
}


let $window = $(window);
$('.section-lead').each(function() { //execute the script separately for each section
  let $parallaxBlock = $(this);
  let parallaxFunc = function() {
    if ($window.width() >= 980) { //if window width >= 768
      let offset = $parallaxBlock.offset().top; //distance from the beginning of the document to the section
      let scrollTop = $window.scrollTop(); //scrolled distance
      let yPos = -(offset - scrollTop)/2; //consider the offset
      let coords = 'right '+ yPos + 'px';
      $parallaxBlock.css('background-position', coords); //set the offset
    } else {
      $parallaxBlock.css('background-position', 'right'); //disable parallax on small screens
    }
  };
  parallaxFunc(); //execute our function on page load

  $window.on('scroll', function() {
    parallaxFunc(); //and when scrolling
  });

});


// Example starter JavaScript for disabling form submissions if there are invalid fields
(function () {
  'use strict'

  // Fetch all the forms we want to apply custom Bootstrap validation styles to
  var forms = document.querySelectorAll('.needs-validation')

  // Loop over them and prevent submission
  Array.prototype.slice.call(forms)
      .forEach(function (form) {
        form.addEventListener('submit', function (event) {
          if (!form.checkValidity()) {
            event.preventDefault()
            event.stopPropagation()
          }

          form.classList.add('was-validated')
        }, false)
      })
})()


jQuery(document).ready(function() {

  $('.popup-01-open').click(function(e) {
    e.preventDefault();
    $('.popup-01-overlay').addClass('active');
  });

  $(document).mouseup( function(e){
    const hidden = $('.popup-01');
    if (!hidden.is(e.target)
        && hidden.has(e.target).length === 0 ) {
      $('.popup-01-overlay').removeClass('active');
    }
  });

  $('.popup-01-close').click(function(e) {
    $('.popup-01-overlay').removeClass('active');
  });

});
