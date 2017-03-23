// The webpage starts in the Investigation Mode
$( document ).ready(function()
{
//  modeInvestigation("Mode: Investigation");
  modeCreation("Mode: Creation");
});

// Depending on the selected Mode (modeDropdown)
// it calls the correspondend onclick-related function
function refresh()
{
    var button = document.getElementById('modeDropdown');
    mode = $(button).attr('mode');
    window.location.reload(false);
    if (mode == 'I') {
       modeInvestigation("Mode: Investigation");
    }
    if (mode == 'C') {
      modeCreation("Mode: Creation");
    }
}

function resetButtons(container)
{
    var c = document.getElementById(container);
    var elems = c.getElementsByClassName('btn-success');
    var i;
    for (i = 0; i < elems.length; i++) {
      $(elems[i]).removeClass('btn-success');
    }
}

function enableButton(button_name)
{
    var c = document.getElementById(button_name);
    $(c).removeClass('disabled');
}

function hideColDiv(container)
{
    var c = document.getElementById(container);
    var elems = c.getElementsByClassName('col-md-20');
    var i;
    for (i = 0; i < elems.length; i++) {
      $(elems[i]).hide();
    }
}

function selectButton(button)
{
  $(button).addClass('btn-success');
}

function selectListItem(item)
{
  var selected = ''
  if ($(item).attr('class') == 'list-group-item')  {
      $(item).addClass('list-group-item-warning');
      selected = 'True';
  }
  else { $(item).removeClass('list-group-item-warning');
      selected = 'False';}
  return selected
}

function selectedElemsInGroupList(item_name)
{
  var elems = [];
  var elem = document.getElementById(item_name);
  if (elem) {
    elems = elem.getElementsByClassName('list-group-item-warning');
  }
  return elems
}

// function fired when the Investigation Mode is selected
// by clicking #modeDropdown
function modeInvestigation(val)
{
 // change the name and mode of the button modeDropdown
   var y = document.getElementById('modeDropdown');
  //  y.innerText = val + '<span class="caret"></span>';
   $(y).html(val + '<span class="caret"></span>');
   y.setAttribute("mode", 'I');

   // hide's and show's
    $('#divCreation').hide();
    $('#creation_buttons_col').hide();
    // $('#investigation_correspondence_col').hide();
    // $('#views-row').hide();
    hideColDiv('divInvestigation');

    // reset all buttons in the investigation mode to primary
    $('#investigation_buttons_col').show();
    $('#divInvestigation').show();
    resetButtons('investigation_buttons_col');

    // CALL THE GRAPHS FUNCTION FOR LOADING GRAPHS INTO RESPECTIVE BUTTONS
    $.get('/getgraphs',function(data)
    {
        // $('#investigation_correspondence_col').hide();
        hideColDiv('divInvestigation');
        $('#investigation_buttons_col').html(data);

        // ON CLICK BUTTON FOR DISPLAYING THE LIST OF CORRESPONDENCES
        $('#investigation_buttons_col a').on('click',function()
        {
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

            $('#corresponsence_list_col').html('Loading...');
            $('#investigation_correspondence_col').show();

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
                              //$('#linktarget5').html('Hello');

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

        $('#linksetsDropdown').on('click', function(e)
        {
            resetButtons('investigation_buttons_col');
            selectButton(this);
        });

        $('#lensesDropdown').on('click', function(e)
        {
            resetButtons('investigation_buttons_col');
            selectButton(this);
        });

        $('#viewsDropdown').on('click', function(e)
        {
            resetButtons('investigation_buttons_col');
            selectButton(this);

            $('#investigation_correspondence_col').hide();
            $('#views-row').show();
            $('#views-results').html('This is where the server response will appear.');

            $('#link14').on('click', function(e)
            {
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
function modeCreation(val)
{
 // change the name and mode of the button modeDropdown
   var y = document.getElementById('modeDropdown');
   $(y).html(val + '<span class="caret"></span>');
   y.setAttribute("mode", 'C');

   // hide's and show's
   $('#divInvestigation').hide();
   $('#investigation_buttons_col').hide();
   $('#creation_buttons_col').show();
   $('#loading').hide();

   // reset all buttons in the creation mode to primary
   hideColDiv('divCreation');
   $('#divCreation').show();
   resetButtons('creation_buttons_col');

   // set actions after clicking the Linkset Button
   $('#creationLinksetButton').on('click',function(e)
   {
     hideColDiv('divCreation');
     resetButtons('creation_buttons_col');
     selectButton(this);

     $.get('/getrquestions',function(data)
     {
       $('#creation_linkset_col').show();
       $('#button_creation_linkset_col').html(data);

        // select a research question
       $('#button_creation_linkset_col a').on('click',function()
       {
         refresh_create_linkset();
         enableButton('createLinksetButton');
         var rq_uri = $(this).attr('uri');
         var rq_label = $(this).attr('label');
         $('#creation_linkset_selected_RQ').html(rq_label);

         // get graphs and load into the graph-buttons
         $('#creation_linkset_row').show();
         $('#loading').show();
         $.get('/getsourcesperrq',data = {'rq_uri': rq_uri}, function(data)
         {
           $('#loading').hide();
           // load the rendered template into ...
           $('#button-src-col').html(data);
           $('#button-trg-col').html(data);

           // set actions after clicking one of the GRAPHS
           // particularly in the creation_source_col
           $('#creation_source_col a').on('click',function()
           {
              refresh_create_linkset(mode='source');
              // get the graph uri and label from the clicked element
              var graph_uri = $(this).attr('uri');
              var graph_label = $(this).attr('label');

              // Attribute the uri of the selected graph to the div
              // where the name/label is displayed
              var elem = document.getElementById('src_selected_graph');
              elem.setAttribute("uri", graph_uri);
              $('#src_selected_graph').html(graph_label);
              $('#src_selected_entity-type').html('Select an Entity Type');

              $.get('/getentitytyperq',data={'rq_uri': rq_uri, 'graph_uri': graph_uri},function(data)
              {
                  // load the rendered template into column #button-src-entity-type-col
                  $('#button-src-entity-type-col').html(data);

                   // set actions after clicking one of the predicates
                   // in the #src_predicates_col
                  $('#button-src-entity-type-col a').on('click',function()
                  {
                      // get the graph uri and label from the clicked element
                      var pred_uri = $(this).attr('uri');
                      var pred_label = $(this).attr('label');

                      // Attributes the uri of the selected predicate to the div
                      // where the name is displayed
                      var elem = document.getElementById('src_selected_entity-type');
                      elem.setAttribute("uri", pred_uri);
                      $('#src_selected_entity-type').html(pred_label);
                  });
              });

              // Exit a waiting message for the user to know loading time
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
                  $('#src_predicates_col li').on('click',function()
                  {
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
           $('#creation_target_col a').on('click',function()
           {
              refresh_create_linkset(mode='target');
              // get the graph uri and label from the clicked element
              var graph_uri = $(this).attr('uri');
              var graph_label = $(this).attr('label');

              // Attributes the uri of the selected graph to the div
              // where the name is displayed
              var elem = document.getElementById('trg_selected_graph');
              elem.setAttribute("uri", graph_uri);
              $('#trg_selected_graph').html(graph_label);
              $('#trg_selected_entity-type').html('Select an Entity Type');

              $.get('/getentitytyperq',data={'rq_uri': rq_uri, 'graph_uri': graph_uri},function(data)
              {
                  // load the rendered template into column #button-src-entity-type-col
                  $('#button-trg-entity-type-col').html(data);

                   // set actions after clicking one of the predicates
                   // in the #src_predicates_col
                  $('#button-trg-entity-type-col a').on('click',function()
                  {
                      // get the graph uri and label from the clicked element
                      var pred_uri = $(this).attr('uri');
                      var pred_label = $(this).attr('label');

                      // Attributes the uri of the selected predicate to the div
                      // where the name is displayed
                      var elem = document.getElementById('trg_selected_entity-type');
                      elem.setAttribute("uri", pred_uri);
                      $('#trg_selected_entity-type').html(pred_label);
                  });
              });
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
           $('#creation_method_col a').on('click',function()
           {
              var meth_label = $(this).attr('label');
              if (meth_label == 'identity')
              {
                var elem = document.getElementById('src_selected_pred');
                elem.setAttribute("uri", "http://www.w3.org/1999/02/22-rdf-syntax-ns#type");
                var elem = document.getElementById('trg_selected_pred');
                elem.setAttribute("uri", "http://www.w3.org/1999/02/22-rdf-syntax-ns#type");
                $('#src_selected_pred_row').hide();
                $('#src_list_pred_row').hide();
                $('#trg_selected_pred_row').hide();
                $('#trg_list_pred_row').hide();
              }
              else
              {
                $('#src_selected_pred_row').show();
                $('#src_list_pred_row').show();
                $('#trg_selected_pred_row').show();
                $('#trg_list_pred_row').show();
              }

              // Attribute the label of the selected method to the div
              // where the name is displayed
              var elem = document.getElementById('selected_meth');
              elem.setAttribute("label", meth_label);
              $('#selected_meth').html(meth_label);
           });

           // set actions after clicking the button createLinksetButton
           $('#createLinksetButton').on('click',function()
           {
              $('#linkset_creation_message_col').html("");

              var srcDict = {};
              if (($('#src_selected_graph').attr('uri')) &&
                 ($('#src_selected_pred').attr('uri')) &&
                 ($('#src_selected_entity-type').attr('uri'))  )
              {
                 srcDict = {'graph': $('#src_selected_graph').attr('uri'),
                            'aligns': $('#src_selected_pred').attr('uri'),
                            'entity_datatye': $('#src_selected_entity-type').attr('uri')};
              }

              var trgDict = {};
              if (($('#trg_selected_graph').attr('uri')) &&
                 ($('#trg_selected_pred').attr('uri'))&&
                 ($('#trg_selected_entity-type').attr('uri')) )
              {
                 trgDict = {'graph': $('#trg_selected_graph').attr('uri'),
                            'aligns': $('#trg_selected_pred').attr('uri'),
                            'entity_datatye': $('#trg_selected_entity-type').attr('uri')};
              }

              //var elem = document.getElementById('selected_context_code');
              if ((Object.keys(srcDict).length) &&
                  (Object.keys(trgDict).length) &&
                  ($('#selected_meth').attr('label'))
                  // && (elem.value)
                  )
              {
                  var specs = {
                    'rq_uri': rq_uri,
                    'src_graph': $('#src_selected_graph').attr('uri'),
                    'src_aligns': $('#src_selected_pred').attr('uri'),
                    'src_entity_datatye': $('#src_selected_entity-type').attr('uri'),

                    'trg_graph': $('#trg_selected_graph').attr('uri'),
                    'trg_aligns': $('#trg_selected_pred').attr('uri'),
                    'trg_entity_datatye': $('#trg_selected_entity-type').attr('uri'),

                    'mechanism': $('#selected_meth').attr('label')
                    // ,'context_code': elem.value
                  }

                  var message = "EXECUTING YOUR LINKSET SPECS.\nPLEASE WAIT UNTIL THE COMPLETION OF YOUR EXECUTION";
                  $('#linkset_creation_message_col').html(message);

                  // call function that creates the linkset
                  // HERE!!!!
                  $.get('/createLinkset', specs, function(data)
                  {
                        var obj = JSON.parse(data);
                        $('#linkset_creation_message_col').html(obj.message);
                  });

              }
              else {
                $('#linkset_creation_message_col').html("Some feature is not selected!");
              }
           });
         });
       });
    });
   });

   $('#creationLinksetRefineButton').on('click',function(e)
   {
     hideColDiv('divCreation');
     resetButtons('creation_buttons_col');
     selectButton(this);

   });

   // set actions after clicking the Lens Button
   $('#creationLensButton').on('click',function(e)
   {
     hideColDiv('divCreation');
     resetButtons('creation_buttons_col');
     selectButton(this);

     $.get('/getrquestions',function(data)
     {
       $('#creation_lens_col').show();
       $('#button_rq_creation_lens_col').html(data);

        // select a research question
       $('#button_rq_creation_lens_col a').on('click',function()
       {
        //  refresh_create_lens();
         enableButton('createLensButton');
         refresh_create_lens();
         var rq_uri = $(this).attr('uri');
         var rq_label = $(this).attr('label');
         $('#creation_lens_selected_RQ').html(rq_label);

         $('#creation_lens_row').show();

         // set actions after clicking one of the Operators
         // particularly in the #creation_operator_col
         $('#creation_operator_col a').on('click',function()
         {
            var operator_label = $(this).attr('label');

            // Attributes the label of the selected operator to the div
            // where the name is displayed
            var elem = document.getElementById('selected_operator');
            elem.setAttribute("label", operator_label);
            $('#selected_operator').html(operator_label);

            var description = '';
            if (operator_label == 'union')
            {
                description = 'The operator UNION bla bla bla bla bla bla bla bla bla bla bla bla bla bla bla bla bla bla bla';
            }
            else if (operator_label == 'intersection')
            {
                description = 'The operator INTERSECTION bla bla bla bla bla bla bla bla bla bla bla bla bla bla bla bla bla bla bla';
            }
            else if (operator_label == 'transitive')
            {
                description = 'The operator TRANSITIVE bla bla bla bla bla bla bla bla bla bla bla bla bla bla bla bla bla bla bla';
            }
            $('#selected_operator_desc').html(description);
         });

         $('#loading2').show();
         $.get('/getgraphsperrqtype',data={'rq_uri': rq_uri,
                                'type': 'linkset',
                                'template': 'list_group.html'},function(data)
         {
           $('#loading2').hide();
           $('#creation_lens_linkset_selection_col').html(data);

           // set actions after clicking a graph in the list
           $('#creation_lens_linkset_selection_col a').on('click',function()
            { selectListItem(this); });
         });

         $.get('/getgraphsperrqtype',data={'rq_uri': rq_uri,
                                'type': 'lens',
                                'template': 'list_group.html'},function(data)
         {
           $('#loading2').hide();
           $('#creation_lens_lens_selection_col').html(data);

           // set actions after clicking a graph in the list
           $('#creation_lens_lens_selection_col a').on('click',function()
            { selectListItem(this); });
         });

         // set actions after clicking the button createLensButton
         $('#createLensButton').on('click',function()
         {
            var elems = selectedElemsInGroupList('creation_lens_linkset_selection_col');
            var i;
            var graphs = []
            for (i = 0; i < elems.length; i++) {
              graphs.push($(elems[i]).attr('uri'));
            }
            elems = selectedElemsInGroupList('creation_lens_lens_selection_col');
            var i;
            for (i = 0; i < elems.length; i++) {
              graphs.push($(elems[i]).attr('uri'));
            }

            if ((graphs.length > 0) &&
                ($('#selected_operator').attr('label')))
            {
                var specs = {'rq_uri': rq_uri,
                            'graphs[]': graphs,
                            'operator': $('#selected_operator').attr('label')};

                var message = "EXECUTING YOUR LENS SPECS.<br/>PLEASE WAIT UNTIL THE COMPLETION OF YOUR EXECUTION";
                $('#lens_creation_message_col').html(message);

                // call function that creates the linkset
                $.get('/createLens', specs, function(data)
                {
                    var obj = JSON.parse(data);
                    $('#lens_creation_message_col').html(obj.message);
                });
            }
            else {
              $('#lens_creation_message_col').html("Some feature is not selected!");
            }
         });
       });
     });
   });

   // set actions after clicking the View Button
   $('#creationViewButton').on('click',function(e)
   {
     hideColDiv('divCreation');
     $('#creation_view_col').show();
     resetButtons('creation_buttons_col');
     selectButton(this);

     $.get('/getrquestions',function(data)
     {
       $('#creation_view_col').show();
       $('#button_rq_creation_view_col').html(data);

        // select a research question
       $('#button_rq_creation_view_col a').on('click',function()
       {
        //  refresh_create_lens();
         enableButton('createViewButton');
         refresh_create_lens();
         var rq_uri = $(this).attr('uri');
         var rq_label = $(this).attr('label');
         $('#creation_view_selected_RQ').html(rq_label);

         $('#creation_view_row').show();

         //  $('#loading4').show();
         $.get('/getsourcesperrq',data={'rq_uri': rq_uri,
                                'type': 'dataset',
                                'template': 'list_group.html'},function(data)
         {
          //  $('#loading4').hide();
           $('#creation_view_dataset_col').html(data);

           // set actions after clicking a graph in the list
           $('#creation_view_dataset_col a').on('click',function()
           {
              var graph_uri = $(this).attr('uri');
              var graph_label = $(this).attr('label');
              //selectListItem(this);

              // $('#creation_view_datasetdetails_row').show();
              $('#creation_view_predicates_msg_col').html('Select <b>' + graph_label + '</b> predicates:')
              // Exihit a waiting message for the user to know loading time
              // might be long.
              $('#creation_view_predicates_col').html('Loading...');
              // get the distinct predicates and example values of a graph
              // into a list group
              $.get('/getpredicates',data={'dataset_uri': graph_uri},function(data)
              {
                   // load the rendered template into the column #creation_view_predicates_col
                  $('#creation_view_predicates_col').html(data);

                  // set actions after clicking one of the predicates
                  $('#creation_view_predicates_col li').on('click',function()
                  {
                    var pred_uri = $(this).attr('uri');
                    var pred_label = $(this).attr('label');


                    elem = document.getElementById(pred_uri);
                    if (elem) {}
                    else {
                      var item = '<li class="list-group-item" pred_uri="' + pred_uri
                                + '" graph_uri="' + graph_uri
                                + '"><span class="list-group-item-heading"><b>'
                                + graph_label + '</b>: ' + pred_label + '</span></li>';

                      $('#creation_view_selected_predicates_group').append(item);
                    }

                    $('#creation_view_selected_predicates_group li').on('ondblclick',function()
                    {
                        // not working yet
                        alert('here');
                        var id = $(this).attr('id');
                        var element = document.getElementById(id);
                        element.parentNode.removeChild(element);
                    });

                  });
              });

           });
         });

        //  $('#loading4').show();
         $.get('/getgraphsperrqtype',data={'rq_uri': rq_uri,
                                'type': 'linkset',
                                'template': 'list_group.html'},function(data)
         {
          //  $('#loading4').hide();
           $('#creation_view_linkset_col').html(data);

           // set actions after clicking a graph in the list
           $('#creation_view_linkset_col a').on('click',function()
           {
              var uri = $(this).attr('uri');
              selectListItem(this);
           });
          });

         $('#loading4').show();
         $.get('/getgraphsperrqtype',data={'rq_uri': rq_uri,
                                'type': 'lens',
                                'template': 'list_group.html'},function(data)
         {
           $('#loading4').hide();
           $('#creation_view_lens_col').html(data);

           // set actions after clicking a graph in the list
           $('#creation_view_lens_col a').on('click',function()
           {
              var uri = $(this).attr('uri');
              selectListItem(this);

              // var selectedLenses = []
              // var elems = selectedElemsInGroupList('creation_view_lens_col');
              // var i;
              // if (elems.length > 0) {
              //     for (i = 0; i < elems.length; i++) {
              //       selectedLenses.push($(elems[i]).attr('uri'));
              //     }
              // }
            });
         });

          // set actions after clicking the button createLensButton
          $('#createViewButton').on('click',function()
          {
             var elems = selectedElemsInGroupList('creation_view_linkset_col');
             var i;
             var view_lens = []
             for (i = 0; i < elems.length; i++) {
               view_lens.push($(elems[i]).attr('uri'));
             }
             elems = selectedElemsInGroupList('creation_view_lens_col');
             for (i = 0; i < elems.length; i++) {
               view_lens.push($(elems[i]).attr('uri'));
             }

            //  alert(view_lens);

             var view_filter = []
             var elem = document.getElementById('creation_view_selected_predicates_group');
             if (elem) {
                elems = elem.getElementsByClassName('list-group-item');
             }
             var dict = {};
             for (i = 0; i < elems.length; i++) {
               dict = {'ds': $(elems[i]).attr('graph_uri'),
                      'att': $(elems[i]).attr('pred_uri') };
               view_filter.push( JSON.stringify(dict));
             }

            //  alert(view_filter);

             if ((view_lens.length > 0) && (view_filter.length > 0))
             {
                 var specs = {'rq_uri': rq_uri,
                              'view_lens[]': view_lens,
                              'view_filter[]': view_filter};

                //  alert("1");
                 // call function that creates the linkset
                 $.get('/createView', specs, function(data)
                 {
                    // alert("2");
                     var obj = JSON.parse(data);
                     $('#view_creation_message_col').html(obj.message);
                 });
             }
             else {
               $('#view_creation_message_col').html("Some feature is not selected!");
             }
          });

       });
     });
   });

      // set actions after clicking the View Button
   $('#creationIdeaButton').on('click',function(e)
   {
     hideColDiv('divCreation');
     $('#creation_idea_col').show();
     resetButtons('creation_buttons_col');
     selectButton(this);

     $('#createIdeaButton').on('click',function()
     {
        var rq_input = document.getElementById('reserach_question');
        $.get('/insertrq',data={'question': rq_input.value},function(data){
            var obj = JSON.parse(data)
            var rq_up_btn = document.getElementById('updateIdeaButton');
            rq_up_btn.setAttribute("rq_uri", obj.rq);

            $('#idea_creation_message_col').html(obj.msg);

            $('#creation_idea_update_col').show();
        });

        $.get('/getgraphsentitytypes',function(data)
        {
            $('#creation_idea_graphtype_list').html(data);

       // set actions after clicking a graph in the list
            $('#creation_idea_graphtype_list li').on('click',function()
            {
               //var uri = $(this).attr('uri');
               $('#creation_idea_selected_graphtype_list').append(this);

               $('#creation_idea_selected_graphtype_list li').on('click',function()
                {
                    //var uri = $(this).attr('uri');
                    $('#creation_idea_graphtype_list').append(this);

                });
            });
        });

       $('#updateIdeaButton').on('click',function()
       {
            var elem = document.getElementById('creation_idea_selected_graphtype_list');
            var elems = elem.getElementsByClassName('list-group-item');

            var i;
            var list = []
            var dict = {}
            for (i = 0; i < elems.length; i++) {
              dict = {'graph':$(elems[i]).attr('uri'),
                      'type':$(elems[i]).attr('type_uri') }
              list.push(JSON.stringify(dict));
            }

            $.get('/updaterq',data={'rq_uri': $(this).attr('rq_uri'), 'list[]': list},function(data)
            {
                $('#idea_update_message_col').html(data);
            });

        });



     });

   });

}


function refresh_create_linkset(mode='all')
{
    var elem = Object;
    $('#linkset_creation_message_col').html("");
    if (mode == 'all')
    {
      elem = document.getElementById('src_selected_graph');
      $('#src_selected_graph').html("Select a Graph");
      elem.setAttribute('uri', '');

      elem = document.getElementById('trg_selected_graph');
      $('#trg_selected_graph').html("Select a Graph");
      elem.setAttribute('uri', '');

      elem = document.getElementById('selected_meth');
      $('#selected_meth').html("Select a Method");
      elem.setAttribute('label', '');
    }

    if (mode == 'all' || mode == 'source')
    {
      elem = document.getElementById('src_selected_entity-type');
      $('#src_selected_entity-type').html("Select an Entity Type");
      elem.setAttribute('uri', '');
      //alert($('#src_selected_entity-type').attr("uri"));

      elem = document.getElementById('src_selected_pred');
      $('#src_selected_pred').html('Select a Property + <span style="color:blue"><strong> example value </strong></span>');
      elem.setAttribute('uri', '');
      //alert($('#src_selected_pred').attr("uri"));

      $('#src_predicates_col').html('');
    }

    if (mode == 'all' || mode == 'target')
    {
      elem = document.getElementById('trg_selected_entity-type');
      $('#trg_selected_entity-type').html("Select an Entity Type");
      elem.setAttribute('uri', '');

      elem = document.getElementById('src_selected_pred');
      $('#trg_selected_pred').html('Select a Property + <span style="color:blue"><strong> example value </strong></span>');
      elem.setAttribute('uri', '');

      $('#trg_predicates_col').html('');
    }
}

function refresh_create_lens(mode='all')
{
    var elem = Object;
    $('#lens_creation_message_col').html("");
    $('#selected_operator').html("Select a Operator");
    $('#selected_operator_desc').html("Operator Description");

    // if (mode == 'all')
    // {
    //   elem = document.getElementById('src_selected_graph');
    //   $('#src_selected_graph').html("Select a Graph");
    //   elem.setAttribute('uri', '');
    // }
    //
    // if (mode == 'all' || mode == 'source')
    // {
    //   elem = document.getElementById('src_selected_entity-type');
    //   $('#src_selected_entity-type').html("Select an Entity Type");
    //   elem.setAttribute('uri', '');
    // }

}


              // if (selectedLenses) {
              //   $.get('/gettargetdatasets',data={'selectedLenses[]': selectedLenses},function(data)
              //   {
              //      $("#creation_view_dataset_col").html(data);
              //
              //      $('#creation_view_dataset_col a').on('click',function()
              //      {
              //         var graph_uri = $(this).attr('uri');
              //         var graph_label = $(this).attr('label');
              //
              //         $('#creation_view_predicates_msg_col').html('Select <b>' + graph_label + '</b> predicates:')
              //         // Exihit a waiting message for the user to know loading time
              //         // might be long.
              //         $('#creation_view_predicates_col').html('Loading...');
              //         // get the distinct predicates and example values of a graph
              //         // into a list group
              //         $.get('/getpredicates',data={'dataset_uri': graph_uri},function(data)
              //         {
              //              // load the rendered template into the column #creation_view_predicates_col
              //             $('#creation_view_predicates_col').html(data);
              //
              //             // set actions after clicking one of the predicates
              //             $('#creation_view_predicates_col li').on('click',function()
              //             {
              //               var pred_uri = $(this).attr('uri');
              //               var pred_label = $(this).attr('label');
              //
              //               elem = document.getElementById(pred_uri);
              //               if (elem) {}
              //               else {
              //                 var item = '<li class="list-group-item" id="' + pred_uri + '"><span class="list-group-item-heading">'+ graph_label + ': ' + pred_label + '</span></li>';
              //
              //                 $('#creation_view_selected_predicates_group').append(item);
              //               }
              //
              //               $('#creation_view_selected_predicates_group li').on('ondblclick',function()
              //               {
              //                   // not working yet
              //                   alert('here');
              //                   var id = $(this).attr('id');
              //                   var element = document.getElementById(id);
              //                   element.parentNode.removeChild(element);
              //               });
              //             });
              //         });
              //      });
              //   });
              // }
