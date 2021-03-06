function BarcodeScanner(id_suffix, container) {

  var url = undefined;
  var success_callback = undefined;
  var fail_callback = undefined;
  var requirement = undefined;
  var last_page = 0;
  var fetch_items = true;
  var last_barcode = undefined;

  // used when the query returns multiple items
  var matched_items = {};

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

  var SCANNER_HTML = clone;


  var cleanup_data = function() {
    SCANNER_HTML.find('.results').children().remove();
    SCANNER_HTML.find('.results').hide();
    matched_items = {};
    last_barcode = undefined;
    last_page = 0;
  }


  var create_item_row = function(item, barcode) {

    matched_items['r_item_' + item.id] = item;

    var clone = $(document.importNode(
      $('#proto_scanner__result_element')[0].content, true)
    );

    // item thumbnail
    if (item.thumb)
      clone.find('.result-thumb').attr('src', item.thumb);

    var clone_data = clone.find('.result-data');
    clone_data.text(item.name);

    var clone_content = clone.find('.scanner-result-element');

    clone_content[0].dataset.item_id = item.id;

    clone_content.on('click', function (event) {
      // child was clicked
      var target = event.target;
      if (!target.classList.contains('.scanner-result-element'))
        target = target.parentNode;
      var item_id = target.dataset.item_id;
      item = matched_items['r_item_' + item_id];
      success_callback(item, barcode);
      // clean previous query results
      cleanup_data();
    });
    SCANNER_HTML.find('.results').append(clone);

  }


  var fetch_matching = function(barcode) {
    if (last_page == -1) return;

    // hack
    rurl = ""
    if (url == DEFAULT_BARCODE_SCANNER_URL) {
      rurl = url + last_page + '?barcode=' + barcode;
    } else {
      rurl = url + barcode + '/' + last_page;
    }

    $.ajax({
      url: rurl
    })
    .done(function(data) {
      if (fetch_items) {
        // only one element found
        if (data.items.length == 1) {
          success_callback(data.items[0], barcode);
          last_page = -1;
        }
        else {
          // if the first item matches the specified barcode then we dont show multiple results
          if (data.items[0].sku == barcode
            || data.items[0].ean == barcode
            || data.items[0].upc == barcode
          ) {
            success_callback(data.items[0], barcode);
            last_page = -1;
          }
          else {
            SCANNER_HTML.find('.results').show();

            // create the matched items list
            for (var index in data.items) {

              create_item_row(data.items[index], barcode);
            }

            // server returned less than 10 items so we are sure there are no more
            if (data.items.length < 10) {
              last_page = -1;
            } else {
              last_page += 1;
            }

          }

        }
      }
      else
        success_callback(data, barcode);
      SCANNER_HTML.find('.scanner-input').val('');
      SCANNER_HTML.find('.scanner-input').blur();
    })
    .fail(function(data) {
      fail_callback(data, barcode);
    });
  }


  clone.find('.results').on('scroll', function(event) {
    var el = $(event.target);
    if(el.scrollTop() + el.innerHeight() >= el[0].scrollHeight) {
      fetch_matching(last_barcode);
    }
  });



  this.setup = function(_success_callback, _fail_callback, _requirement, _url) {
    fetch_items = false;
    if (!_url) {
      _url = DEFAULT_BARCODE_SCANNER_URL;
      fetch_items = true;
    }

    success_callback = _success_callback;
    fail_callback = _fail_callback;
    requirement = _requirement;
    url = _url;

    $(SCANNER_HTML).on('submit', function(event) {
      event.preventDefault();

      cleanup_data();

      var barcode = SCANNER_HTML.find('.scanner-input').val();

      if ((requirement && requirement(barcode)) || !requirement) {
        fetch_matching(barcode);
        last_barcode = barcode;
      }

      return false;
    });
  }

  return this;
}






// ---------------------------------------------------
// Deprecated, should be removed
// ---------------------------------------------------

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
        if (items) {
          // only one element found
          if (data.items.length == 1) {
            success_callback(data.items[0], barcode);
          }
          else {
            // create the matched items list
            for (var index in data.items) {
              var item = data.items[index];

              var clone = $(document.importNode(
                $('#proto_scanner__result_element')[0].content, true)
              );
              var clone_content = clone.find('.scanner-result-element');
              clone_content.text(item.name);
              clone_content[0].dataset.item_id = item.id;
              //clone.textContent = data.items[index].name;
              scanner.find('.results').append(clone);

              clone_content.on('click', function (event) {
                var item_id = event.target.dataset.item_id;
                item = items['r_item_' + item_id]
                success_callback(item, barcode);
              });
            }
            //success_callback(data.items[0], barcode);
          }
        }
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
