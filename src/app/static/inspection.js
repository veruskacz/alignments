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

            hideColDiv('divInvestigation');
            $('#investigation_correspondence_col').show();
            $('#investigation_correspondence_col').html('Loading...');


            // FUNCTION THAT GETS THE LIST OF CORRESPONDENCES
            $.get('/getcorrespondences',data={'uri': graph_uri, 'label': graph_label,
                                              'graph_menu': graph_menu,
                                              'graph_triples': graph_triples,
                                              'operator': operator,
                                              'alignsMechanism': alignsMechanism},function(data)
            {
                // LOAD THE CORRESPONDENCES DIV WITH THE LIST OF CORRESPONDENCES
                $('#investigation_correspondence_col').html(data);

                // CLICK ON INDIVIDUAL CORRESPONDENCE TO READ DETAILS ABOUT WHY IT
                // WAS CREATED AND VALIDATE OR REJECTS IT
                $("#investigation_correspondence_col a").on('click', function()
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
                        $.get('/getLensDetail1',data=data,function(data)
                        {
                            // DETAIL liST COLUMN
                            $('#details_list_col').html(data);

                            // SOURCE CLICK
                            $("#srcDatasetLI").on('click', function()
                            {
                              var dataset = $(this).attr('dataset');
                              //$('#linktarget5').html('Hello');

                              $.get('/getdatadetails',data={'dataset_uri': dataset, 'resource_uri': sub_uri},function(data)
                              {
                                $('#srcDetails1').html(data);
                              });
                            });

                             // TARGET CLICK
                            $("#trgDatasetLI").on('click', function()
                            {
                              var dataset = $(this).attr('dataset');
                              $.get('/getdatadetails',data={'dataset_uri': dataset, 'resource_uri': obj_uri},function(data)
                              {
                                $('#trgDetails1').html(data);
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

                            // SOURCE CLICK
                            $("#srcDatasetLI").on('click', function()
                            {
                              $.get('/getdatadetails',data={'dataset_uri': subjectTarget_uri, 'resource_uri': sub_uri},function(data)
                              {
                                $('#srcDetails').html(data);
                              });
                            });

                             // TARGET CLICK
                            $("#trgDatasetLI").on('click', function()
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

            hideColDiv('divInvestigation');
            $('#investigation_view_col').show();

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


function showDetails(graph_uri, detailsDict)
{
  // inspect_linkset_linkset_details_col
  var graph_uri = graph_uri;
  var graph_label = graph_uri;
  var subjectTarget = detailsDict.subTarget_stripped.value;
  var objectTarget = detailsDict.objTarget_stripped.value;
  var subjectTarget_uri = detailsDict.subTarget.value;
  var objectTarget_uri = detailsDict.objTarget.value;
  var graph_triples = detailsDict.triples.value;
  var alignsSubjects = detailsDict.s_property.value;
  var alignsObjects = detailsDict.o_property.value;
  var alignsMechanism = detailsDict.mechanism.value;
  var operator = detailsDict.operator.value;;

  hideColDiv('divInvestigation');

  if (operator) // THEN IT IS A LENS
  { div = 'creation_lens_correspondence_col'
  }
  else
  { div = 'creation_linkset_correspondence_col'
  }
  $('#'+div).show();
  $('#'+div).html('Loading...');

  // FUNCTION THAT GETS THE LIST OF CORRESPONDENCES
  $.get('/getcorrespondences',data={'uri': graph_uri, 'label': graph_label,
                                    'graph_triples': graph_triples,
                                    'operator': operator,
                                    'alignsMechanism': alignsMechanism},function(data)
  {
      // LOAD THE CORRESPONDENCES DIV WITH THE LIST OF CORRESPONDENCES
      $('#'+div).html(data);

      // CLICK ON INDIVIDUAL CORRESPONDENCE TO READ DETAILS ABOUT WHY IT
      // WAS CREATED AND VALIDATE OR REJECTS IT
      $('#'+div+" a").on('click', function()
      {
          var item_id = $(this).attr('id');
          var uri = $(this).attr('uri');
          var sub_uri = $(this).attr('sub_uri');
          var obj_uri = $(this).attr('obj_uri');

          //HANDLING THE SELECTION/DE-SELECTION OF CLICKED CORRESPONDENCES
          var parent = findAncestor(this, "list-group");
          var selected = $(parent).attr('target');
          if (selected)
          {
            var elem = document.getElementById(selected);
            // de-selected previously selected item
            selectListItem(elem);
          }
          // select previously selected item
          selectListItem(this);
          // saving the currently selected correspondence
          parent.setAttribute("target",$(this).attr('id'));

          var data = {'uri': uri, 'sub_uri': sub_uri, 'obj_uri': obj_uri,
                            'subjectTarget': subjectTarget,
                            'objectTarget': objectTarget,
                            'alignsSubjects': alignsSubjects,
                            'alignsObjects': alignsObjects}

          // REPLACE WITH A CHECK FOR THE SELECT BUTTON TYPE (LINKSET OR LENS)
          if (operator) // THEN IT IS A LENS
          {
              $.get('/getLensDetail1',data=data,function(data)
              {
                  // DETAIL liST COLUMN
                  $('#details_list_col').html(data);

                  // SOURCE CLICK
                  $("#srcDatasetLI").on('click', function()
                  {
                    var dataset = $(this).attr('dataset');
                    //$('#linktarget5').html('Hello');

                    $.get('/getdatadetails',data={'dataset_uri': dataset, 'resource_uri': sub_uri},function(data)
                    {
                      $('#srcDetails1').html(data);
                    });
                  });

                   // TARGET CLICK
                  $("#trgDatasetLI").on('click', function()
                  {
                    var dataset = $(this).attr('dataset');
                    $.get('/getdatadetails',data={'dataset_uri': dataset, 'resource_uri': obj_uri},function(data)
                    {
                      $('#trgDetails1').html(data);
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

                  // SOURCE CLICK
                  $("#srcDatasetLI").on('click', function()
                  {
                    $.get('/getdatadetails',data={'dataset_uri': subjectTarget_uri, 'resource_uri': sub_uri},function(data)
                    {
                      $('#srcDetails').html(data);
                      $("#srcDetails li").on('click', function()
                      {  selectListItemUniqueWithTarget(this);
                      });
                    });
                  });

                   // TARGET CLICK
                  $("#trgDatasetLI").on('click', function()
                  {
                    $.get('/getdatadetails',data={'dataset_uri': objectTarget_uri, 'resource_uri': obj_uri},function(data)
                    {
                      $('#trgDetails').html(data);
                      $("#trgDetails li").on('click', function()
                      {  selectListItemUniqueWithTarget(this);
                      });
                    });
                  });
              });
          }

          $.get('/getevidence',data={'singleton_uri': uri},function(data)
          {
              $('#evidence_list_col').html(data);
          });

      });

  });
}


function validationSaveOnClick()
{
  // retrieve the uri of the selected singleton
  var lg = document.getElementById('corresp_list_group');
  var graph_uri = $(lg).attr("uri");
  var target = $(lg).attr("target");
  var elem = document.getElementById(target);
  var uri = $(elem).attr("uri");

  // if the validation option selected is reject&refine
  if(document.getElementById('ValidationRefine_btn').checked) {
       // retrieve the selected properties, if any

       // get the selected predicate within the source div
       var selected_elems = selectedElemsInDiv('srcDetails');
       if (selected_elems.length > 0)
       { var pred_source = selected_elems[0];} //assuming only one is selected

       // get the selected predicate within the target div
       var selected_elems = selectedElemsInDiv('trgDetails');
       if (selected_elems.length > 0)
       { var pred_target = selected_elems[0];} //assuming only one is selected

       // if both properties are selected
       if (pred_source && pred_target)
       {
           // load the Edit Panel, "as-if" the button refine wasc clicked
           //  but without realoding, i.e. the selected linkset is maintained
           $('#creation_linkset_correspondence_row').hide();
           btn = document.getElementById('btn_refine_linkset');
           newSelectButton(btn);
           $('#creation_linkset_row').show();
           activateTargetDiv(targetId="refine_linkset_heading",cl="panel-heading");
           loadEditPanel(graph_uri, mode='reject-refine');

           // load the properties selected for refinement
           setAttr('trg_selected_pred','uri',$(pred_target).attr('uri'));
           $('#trg_selected_pred').html($(pred_target).attr('label'));
           setAttr('src_selected_pred','uri',$(pred_source).attr('uri'));
           $('#src_selected_pred').html($(pred_source).attr('label'));
       }
       else
       {
           $('#evidence_message_col').html("Select a pair of properties in the above panel <strong>Details</strong>");
       }
  }
  else
  {
     var validation_text = $('#validation_textbox').val();

     // if the validation option selected is agreement
     if(document.getElementById('ValidationYes_btn').checked)
     {   var predicate = 'http://example.com/predicate/good';
     } else
     // if the validation option selected is disagreement
     if(document.getElementById('ValidationNo_btn').checked)
     {    var predicate = 'http://example.com/predicate/bad';
     }

     // register the agreement comment as evidence
     $.get('/updateevidence',data={'singleton_uri': uri,
                                   'predicate': predicate,
                                   'validation_text': validation_text},
                             function(data){
        // reload the evidences
        $.get('/getevidence',data={'singleton_uri': uri},function(data)
          {
              $('#evidence_list_col').html(data);
          });
     });

  }
}
