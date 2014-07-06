$(document).ready(function(){
    $( "#btn_search" ).on( "click", function() {
//       Section: <input id="search_section" type="text" name="section">
//        Word: <input id="search_word" type="text" name="word">
//        <button id="btn_search">Search!</button>
//    <div id="search_result">
//
//    </div>

        var section = $("#search_section").val();
        var word = $("#search_word").val();

        $.get( "/search/"+section+"/"+word, function( data ) {
          //$( ".result" ).html( data );
            var _list = $("#search_result");
            _list.empty();
            $.each(data["data"], function(i) {
                var li = $('<li/>')
                    .addClass('list-group-item')
                    .css('font-size', '250%')
                    .text(data["data"][i])
                    .appendTo(_list);
            });
        });
    });
      $( "#btn_clear" ).on( "click", function() {
          $("#search_result").empty();
      });

});