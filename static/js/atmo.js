function request({url, type, data={}, ondone=function(){}, params=[]}){
  log("request for: " + type + "::" + url);
  $.ajax({
    url: url,
    type: type,
    data: data,
    cache: false,
    statusCode: {
      400: function() {
        M.toast({html: 'Ошибка 400! Проверьте корректность ввода'})
      },
      404: function() {
        M.toast({html: 'Ошибка 404! Проверьте корректность ввода'})
      },
      409: function() {
        M.toast({html: 'Ошибка 409! Объект уже забронирован.'})
      },
      500: function() {
        M.toast({html: 'Ошибка 500! Произошла ошибка на серере.'})
      },
    }
  })
  .done(function (resp) {
    log(resp);
    ondone(resp, params)
  });
}

function log(msg){
  if(isDebug){console.log(msg)}
}

function includeHTML(fn=null) {
    var z, i, elmnt, file, xhttp;
    /* Loop through a collection of all HTML elements: */
    z = document.getElementsByTagName("*");
    for (i = 0; i < z.length; i++) {
        elmnt = z[i];
        /*search for elements with a certain atrribute:*/
        file = elmnt.getAttribute("w3-include-html");
        if (file) {
          /* Make an HTTP request using the attribute value as the file name: */
          xhttp = new XMLHttpRequest();
          xhttp.onreadystatechange = function() {
            if (this.readyState == 4) {
              if (this.status == 200) {elmnt.innerHTML = this.responseText;}
              if (this.status == 404) {elmnt.innerHTML = "Page not found.";}
              /* Remove the attribute, and call this function once more: */
              elmnt.removeAttribute("w3-include-html");
              includeHTML();
            }
          }
          xhttp.open("GET", file, true);
          xhttp.send();
          /* Exit the function: */
          if(fn){
            setTimeout(fn, 1000);
          }
          return;
        }
    }
}