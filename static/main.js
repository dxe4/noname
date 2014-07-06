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
            $("#search_result");
            console.log(data);
        });


    });
});