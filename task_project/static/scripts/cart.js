$(document).ready((e) => {
  function csrfSafeMethod(method) {
    return /^(GET|HEAD|OPTIONS|TRACE)$/.test(method);
  }
  $.ajaxSetup({
    beforeSend: function (xhr, settings) {
      if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
        xhr.setRequestHeader('X-CSRFToken', csrftoken);
      }
    }
  });

  var button = $('.product__buy__button');
  button.on('click', function(e) {
	 var href= $(this).attr('href');
	  if(href)
		  return true;
    e.preventDefault();
    const url = $(this).attr('data-href');
    const $btn = $(this);


    $.ajax({
      url: url,
      type: 'POST',
      data: {},
      success: (response) => {
          var $addBtns = $btn;
          $addBtns.text("Перейти в корзину");
          $addBtns.addClass('cart_index');
          $addBtns.removeClass('.product__buy__button');
          $addBtns.attr('href', response.cart_url);
		  
      },
      error: (response) => {
        location.reload();
      }
    });
  });


  function updateItem (url, data) {
    $.ajax({
      url: url,
      method: 'POST',
      data: data,
      success: (response) => {
        location.reload();
      }
    });
  }

  var cartLine = $('.item'),
    total = $('.total-block .final .price'),
    cartBadge = $('.navbar__brand__cart .cart__block .cart__image');

  cartLine.each(function () {
    let quantityUp = $(this).find('.jq-number__spin.plus');
    let quantityDown = $(this).find('.jq-number__spin.minus');
    let cartFormUrl = $(this).attr('action');
    let deleteIcon = $(this).find('.close');

    quantityUp.on('click', (e) => {
      let quantityValue = $(this).find('.jq-number__field input').val();
      updateItem(cartFormUrl, {quantity: quantityValue});
    });

    quantityDown.on('click', (e) => {
      let quantityValue = $(this).find('.jq-number__field input').val();
      updateItem(cartFormUrl, {quantity: quantityValue});
    });

    deleteIcon.on('click', (e) => {
      updateItem(cartFormUrl, {quantity: 0});
    });
  });

  // sticky side panel in the basket when scrolling
  if ($('.aside').length) {
    (new StickySidebar('.aside', {
      topSpacing: 20,
      bottomSpacing: 20,
      containerSelector: '.sticky-container',
      innerWrapperSelector: '.right-content',
      minWidth: 990
    }));
  }
});
