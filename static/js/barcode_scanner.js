function create_scanner(id_suffix, container) {
  // clone proto scanner
  var clone = $(document.importNode($('#proto_scanner')[0].content, true));
  var scanner_form_id = 'barcode_scanner_form';
  var scanner_input_id = 'barcode';
  if (id_suffix) {
    scanner_form_id += '__' + id_suffix;
    scanner_input_id += '__' + id_suffix;
  }
  clone.find('.scanner-form').attr('id', scanner_form_id);
  clone.find('.scanner-input').attr('id', scanner_input_id);

  if (container) {
    container.append(clone);
    clone = $('#' + scanner_form_id);
  }
  return clone;
}

function setup_scanner(scanner, success_callback, fail_callback, requirement, url) {

  var items = false;
  if (!url) {
    url = DEFAULT_BARCODE_SCANNER_URL;
    items = true;
  }

  $(scanner).on('submit', function(event) {
    event.preventDefault();

    var barcode = scanner.find('.scanner-input').val();

    if ((requirement && requirement(barcode)) || !requirement) {
      $.ajax({
        url: url + barcode
      })
      .done(function(data) {
        if (items)
          success_callback(data.item, barcode);
        else
          success_callback(data, barcode);
        scanner.find('.scanner-input').val('');
      })
      .fail(function(data) {
        fail_callback(data, barcode);
      });
    }

    return false;
  });
};