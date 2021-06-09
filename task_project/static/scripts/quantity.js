$('.jq-number__spin.minus').click(function () {
  var parentDiv = $(this).parent(),
      quantity = $('.jq-number__field input', parentDiv),
      value = quantity.val();
  if (value > 0) {
      quantity.val(Number(value) - 1);
  };
});
$('.jq-number__spin.plus').click(function () {
  var parentDiv = $(this).parent(),
      quantity = $('.jq-number__field input', parentDiv),
      value = quantity.val();
  quantity.val(Number(value) + 1);
});
