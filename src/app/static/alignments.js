// The webpage starts in the Investigation Mode
$( document ).ready(function()
{
    modeInvestigation("Mode: Investigation");
});

//$.get('/print',function(){});

// function fired when the Investigation Mode is selected
// by clicking #modeDropdown
function modeInvestigation(val){
 // var y = document.getElementsByClassName('btn btn-default dropdown-toggle');
 // var aNode = y[0].innerText=val;
  // alert(val);
 // if (val == 'Mode: Investigation') {
 //    alert("Test");
 // }
    $('#divCreation').hide();
    $('#creation_buttons_col').hide();
    $('#divInvestigation').show();
    $('#investigation_buttons_col').show();
    $('#corresponsence_list_row').hide();
    $('#views-row').hide();

    // CALL THE GRAPHS FUNCTION FOR LOADING GRAPHS INTO RESPECTIVE BUTTONS
    $.get('/getgraphs',function(data)
    {
        $('#corresponsence_list_row').hide();
        $('#investigation_buttons_col').html(data);
        // $('#viewButton').button('toggle');

        // $('#startButton').on('click',function()
        // {
        //     $('#corresponsence_list_row').hide();
        //     window.location.reload(false);
        // });

        // ON CLICK BUTTON FOR DISPLAYING THE LIST OF CORRESPONDENCES
        $('#investigation_buttons_col a').on('click',function()
        {
            // var selectedButton = $(this).attr('aria-labelledby');
            // if (selectedButton == 'linksetsDropdown') {
            //   $('#viewButton').aria-pressed('false');
            //   $('#linksetsDropdown').button('toggle');
            // }
            // else if (selectedButton == 'lensesDropdown') {
            //   $('#lensesDropdown').toggleClass("clicked");
            // }

            var graph_menu = $(this).attr('graph_menu');
            var graph_uri = $(this).attr('uri');
            var graph_label = $(this).attr('label');
            var subjectTarget = $(this).attr('subjectTarget');
            var objectTarget = $(this).attr('objectTarget');
            var subjectTarget_uri = $(this).attr('subjectTarget_uri');
            var objectTarget_uri = $(this).attr('objectTarget_uri');
            var graph_triples = $(this).attr('triples');
            var alignsSubjects = $(this).attr('alignsSubjects');
            var alignsObjects = $(this).attr('alignsObjects');
            var alignsMechanism = $(this).attr('alignsMechanism');
            var operator = $(this).attr('operator');

            $('#views-row').hide();
            $('#corresponsence_list_col').html('Loading...');
            $('#corresponsence_list_row').show();

            // FUNCTION THAT GETS THE LIST OF CORRESPONDENCES
            $.get('/getcorrespondences',data={'uri': graph_uri, 'label': graph_label,
                                              'graph_menu': graph_menu,
                                              'graph_triples': graph_triples,
                                              'operator': operator,
                                              'alignsMechanism': alignsMechanism},function(data)
            {
                // LOAD THE CORRESPONDENCES DIV WITH THE LIST OF CORRESPONDENCES
                $('#corresponsence_list_col').html(data);

                // CLICK ON INDIVIDUAL CORRESPONDENCE TO READ DETAILS ABOUT WHY IT
                // WAS CREATED AND VALIDATE OR REJECTS IT
                $("#corresponsence_list_col a").on('click', function()
                {
                    var uri = $(this).attr('uri');
                    var sub_uri = $(this).attr('sub_uri');
                    var obj_uri = $(this).attr('obj_uri');

                    var data = {'uri': uri, 'sub_uri': sub_uri, 'obj_uri': obj_uri,
                                      'subjectTarget': subjectTarget,
                                      'objectTarget': objectTarget,
                                      'alignsSubjects': alignsSubjects,
                                      'alignsObjects': alignsObjects}

                    // REPLACE WITH A CHECK FOR THE SELECT BUTTON TYPE (LINKSET OR LENS)
                    if (operator) // THEN IT IS A LENS
                    {
                        $.get('/getLensDetail',data=data,function(data)
                        {
                            // DETAIL liST COLUMN
                            $('#details_list_col').html(data);

                            // SOURCE CLICK
                            $("#srcDataset").on('click', function()
                            {
                              var dataset = $(this).attr('dataset');
//                              $('#linktarget5').html('Hello');

                              $.get('/getdatadetails',data={'dataset_uri': dataset, 'resource_uri': sub_uri},function(data)
                              {
                                $('#srcDetails').html(data);
                              });
                            });

                             // TARGET CLICK
                            $("#trgDataset").on('click', function()
                            {
                              var dataset = $(this).attr('dataset');
                              $.get('/getdatadetails',data={'dataset_uri': dataset, 'resource_uri': obj_uri},function(data)
                              {
                                $('#trgDetails').html(data);
                              });
                            });

                        });
                    }
                    else
                    {
                        // GEt CORRESPONDENCE DETAILS
                        $.get('/getdetails',data=data,function(data)
                        {
                            // DETAIL liST COLUMN
                            $('#details_list_col').html(data);

                            // var data2 = {'subjectTarget': subjectTarget,
                            //             'alignsSubjects': subjectTarget,
                            //             'objectTarget': subjectTarget,
                            //             'alignsObjects': subjectTarget}
                            // $('#detailsHeading').html(data2);

                            // SOURCE CLICK
                            $("#srcDataset").on('click', function()
                            {
                              // var message = data2['subjectTarget']; //$('#messageInput2').val();
                            	// $('#linktarget5').html(message);
                              // $('#trgDataset').hide();
                              // $('#srcDataset').show();
                              $.get('/getdatadetails',data={'dataset_uri': subjectTarget_uri, 'resource_uri': sub_uri},function(data)
                              {
                                $('#srcDetails').html(data);
                              });
                            });

                             // TARGET CLICK
                            $("#trgDataset").on('click', function()
                            {
                              $.get('/getdatadetails',data={'dataset_uri': objectTarget_uri, 'resource_uri': obj_uri},function(data)
                              {
                                $('#trgDetails').html(data);
                              });
                            });
                        });
                    }

                    $.get('/getevidence',data={'singleton_uri': uri},function(data)
                    {
                      $('#evidence_list_col').html(data);

                      $('#ValidationYes_btn').on('click', function(e)
                      {
                         var validation_text = $('#validation_textbox').val();
                         var predicate = 'http://example.com/predicate/good';
                         $.get('/updateevidence',data={'singleton_uri': uri, 'predicate': predicate, 'validation_text': validation_text},function(data){});
                       });

                      $('#ValidationNo_btn').on('click', function(e)
                      {
                           var validation_text = $('#validation_textbox').val();
                         var predicate = 'http://example.com/predicate/bad';
                         $.get('/updateevidence',data={'singleton_uri': uri, 'predicate': predicate, 'validation_text': validation_text},function(data){});
                       });

                    });

                });

            });
        });

        $('#viewButton').on('click', function(e)
        {
            // $('#viewButton').aria-pressed('true');
            // $('#viewButton').button('toggle');
            $('#corresponsence_list_row').hide();
            $('#views-row').show();
            $('#views-results').html('This is where the server response will appear.');

            $('#link14').on('click', function(e){

              var query = $('#query14').val();
              $.get('/sparql',data={'query': query}, function(data)
              {
                $('#views-results').html(data);
              });

            });

        });
    });
}

// function fired when the Creation Mode is selected
// by clicking #modeDropdown
function modeCreation(val){
 // var y = document.getElementsByClassName('btn btn-default dropdown-toggle');
 // var aNode = y[0].innerText=val;
 $('#divInvestigation').hide();
 $('#investigation_buttons_col').hide();
 $('#creation_buttons_col').show();
 $('#divCreation').show();
 $('#loading').hide();
 $('#creation_linkset_col').hide();
 $('#creation_lens_col').hide();
 $('#creation_view_col').hide();


 $('#creationLinksetButton').on('click',function(e){
   $('#creation_view_col').hide();
   $('#creation_lens_col').hide();
   // get graphs and load into the graph-buttons
   $('#loading').show();
   $.get('/getgraphspertype',function(data)
   {
     $('#loading').hide();
     $('#creation_linkset_col').show();
     // load the rendered template into the column #creation_col
    //  $('#creation_linkset_col').html(data);
     $('#button-src-col').html(data);
     $('#button-trg-col').html(data);

     // set actions after clicking one of the GRAPHS
     // particularly in the creation_source_col
     $('#creation_source_col a').on('click',function(){
        // get the graph uri and label from the clicked element
        var graph_uri = $(this).attr('uri');
        var graph_label = $(this).attr('label');

        // Attribute the uri of the selected graph to the div
        // where the name/label is displayed
        var elem = document.getElementById('src_selected_graph');
        elem.setAttribute("uri", graph_uri);
        $('#src_selected_graph').html(graph_label);

        // Exihit a waiting message for the user to know loading time
        // might be long.
        $('#src_predicates_col').html('Loading...');
        // get the distinct predicates and example values of a graph
        // into a list group
        $.get('/getpredicates',data={'dataset_uri': graph_uri},function(data)
        {
            $('#src_selected_pred').show();
             // load the rendered template
             // into the column #src_predicates_col
            $('#src_predicates_col').html(data);

             // set actions after clicking one of the predicates
             // in the #src_predicates_col
            $('#src_predicates_col li').on('click',function(){
                // get the graph uri and label from the clicked element
                var pred_uri = $(this).attr('uri');
                var pred_label = $(this).attr('label');

                // Attributes the uri of the selected predicate to the div
                // where the name is displayed
                var elem = document.getElementById('src_selected_pred');
                elem.setAttribute("uri", pred_uri);
                $('#src_selected_pred').html(pred_label);
            });

        });
     });

     // set actions after clicking one of the GRAPHS
     // particularly in the creation_target_col
     $('#creation_target_col a').on('click',function(){
        // get the graph uri and label from the clicked element
        var graph_uri = $(this).attr('uri');
        var graph_label = $(this).attr('label');

        // Attributes the uri of the selected graph to the div
        // where the name is displayed
        var elem = document.getElementById('trg_selected_graph');
        elem.setAttribute("uri", graph_uri);
        $('#trg_selected_graph').html(graph_label);

        // Exihit a waiting message for the user to know loading time
        // might be long.
        $('#trg_predicates_col').html('Loading...');
        // get the distinct predicates and example values of a graph
        // into a list group
        $.get('/getpredicates',data={'dataset_uri': graph_uri},function(data)
        {
            $('#trg_selected_pred').show();
             // load the rendered template
             // into the column #trg_predicates_col
            $('#trg_predicates_col').html(data);

             // set actions after clicking one of the predicates
             // in the #src_predicates_col
            $('#trg_predicates_col li').on('click',function(){
                // get the graph uri and label from the clicked element
                var pred_uri = $(this).attr('uri');
                var pred_label = $(this).attr('label');

                // Attributes the uri of the selected predicate to the div
                // where the name is displayed
                var elem = document.getElementById('trg_selected_pred');
                elem.setAttribute("uri", pred_uri);
                $('#trg_selected_pred').html(pred_label);
            });
        });
     });

     // set actions after clicking one of the Method
     // particularly in the #creation_method_col
     $('#creation_method_col a').on('click',function(){
        var meth_label = $(this).attr('label');
        var meth_uri = $(this).attr('uri');
        // Display the selected method in the corresponding div
        // Attributes the uri of the selected predicate to the div
        // where the name is displayed
        var elem = document.getElementById('selected_meth');
        elem.setAttribute("uri", meth_uri);
        $('#selected_meth').html(meth_label);
     });

     // set actions after clicking the button createLinksetButton
     $('#createLinksetButton').on('click',function(){

        $('#linkset_creation_message_col').html("");


        var srcDict = {};
        if (($('#src_selected_graph').attr('uri')) &&
           ($('#src_selected_pred').attr('uri')))
        {
           srcDict = {'graph': $('#src_selected_graph').attr('uri'),
                      'aligns': $('#src_selected_pred').attr('uri')};
        }

        var trgDict = {};
        if (($('#trg_selected_graph').attr('uri')) &&
           ($('#trg_selected_pred').attr('uri')))
        {
           trgDict = {'graph': $('#trg_selected_graph').attr('uri'),
                      'aligns': $('#trg_selected_pred').attr('uri')};
        }

        if ((Object.keys(srcDict).length) &&
            (Object.keys(trgDict).length) &&
            ($('#selected_meth').attr('uri')))
        {
            var dict = {'source': srcDict,
                        'target': trgDict,
                        'mechanism': $('#selected_meth').attr('uri')};

            // call function that creates the linkset
            // HERE!!!!

            $('#linkset_creation_message_col').html("Linkset is created!");
        }
        else {
          $('#linkset_creation_message_col').html("Some feature is not selected!");
        }
     });
   });
 });

 $('#creationLensButton').on('click',function(e){
   $('#creation_linkset_col').hide();
   $('#creation_view_col').hide();
   $('#creation_lens_col').show();
 });

 $('#creationViewButton').on('click',function(e){
   $('#creation_linkset_col').hide();
   $('#creation_lens_col').hide();
   $('#creation_view_col').show();

 });

}
