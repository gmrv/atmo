function ajget(url, fn_ondone=function(){}, params=[]){
  log(`request for url: ${url}`);
  $.ajax({
    url: url,
    cache: false,
    statusCode: {
      400: function() {
        $('#booking-time')[0].style.background = "pink";
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
    fn_ondone(resp, params)
  });
}

function log(msg){
  if(isDebug){console.log(msg)}
}