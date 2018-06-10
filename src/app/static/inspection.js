
function showDetails(rq_uri, graph_uri, detailsDict, filter_uri='', filter_term='')
{
  var graph_label = graph_uri;
  var subjectTarget = detailsDict.subTarget_stripped.value;
  var objectTarget = detailsDict.objTarget_stripped.value;
  var subjectTarget_uri = detailsDict.subTarget.value;
  var objectTarget_uri = detailsDict.objTarget.value;
  var graph_triples = detailsDict.triples.value;
  var alignsSubjects = detailsDict.s_property.value;
  var alignsObjects = detailsDict.o_property.value;
  var alignsMechanism = detailsDict.mechanism.value;
  var operator = detailsDict.operator.value;
  var alignsSubjectsList = detailsDict.s_property_list.value
  var alignsObjectsList = detailsDict.o_property_list.value
  var crossCheckSubject = detailsDict.s_crossCheck_property.value
  var crossCheckObject = detailsDict.o_crossCheck_property.value

  hideColDiv('divInvestigation');

  if (operator) // THEN IT IS A LENS
  { div = 'creation_lens_correspondence_col';
    graph_menu = 'lens';
  }
  else
  { div = 'creation_linkset_correspondence_col';
    graph_menu = 'linkset';
  }
  $('#'+div).show();
  $('#'+div).html('Loading...');

  // FUNCTION THAT GETS THE LIST OF CORRESPONDENCES
  $.get('/getcorrespondences2',data={'rq_uri': rq_uri,
                                    'graph_uri': graph_uri,
                                    'filter_uri': filter_uri,
                                    'filter_term': filter_term,
                                    'label': graph_label,
                                    'graph_menu': graph_menu,
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
          selectListItemUniqueWithTarget(this);

          var data = {'uri': uri, 'graph_uri': graph_uri,
                            'sub_uri': sub_uri, 'obj_uri': obj_uri,
                            'subjectTarget': subjectTarget,
                            'objectTarget': objectTarget,
                            'alignsSubjects': alignsSubjects,
                            'alignsObjects': alignsObjects,
                            'alignsSubjectsList': alignsSubjectsList,
                            'alignsObjectsList': alignsObjectsList,
                            'crossCheckSubject': crossCheckSubject,
                            'crossCheckObject': crossCheckObject,
                            'alignsMechanism': alignsMechanism
                            }

          // REPLACE WITH A CHECK FOR THE SELECT BUTTON TYPE (LINKSET OR LENS)
          if (operator) // THEN IT IS A LENS
          {
              var evidence_div = '#lens_evidence_list_col';

              $('#inspect_linkset_linkset_details_col').html('');
              $('#inspect_linkset_linkset_details_col').hide();
              $('#inspect_linkset_cluster_details_col').html('');
              $('#inspect_linkset_cluster_details_col').hide();
              $('#inspect_lens_lens_details_col').show();

              $('#lens_details_list_col').html('Loading...');
              $.get('/getLensDetail1',data=data,function(data)
              {
                  // DETAIL liST COLUMN
                  $('#lens_details_list_col').html(data);

                  // SOURCE CLICK
                  $("#srcDatasetLS").on('click', function()
                  {
                    var dataset = $(this).attr('dataset');

                    $('#srcDetailsLS').html('Loading...');
                    $.get('/getdatadetails',data={'dataset_uri': dataset, 'resource_uri': sub_uri},function(data)
                    {
                      $('#srcDetailsLS').html(data);
                      $("#srcDetailsLS li").on('click', function()
                      {  selectListItemUniqueWithTarget(this);
                      });
                    });
                  });

                   // TARGET CLICK
                  $("#trgDatasetLS").on('click', function()
                  {
                    var dataset = $(this).attr('dataset');
                    $('#trgDetailsLS').html('Loading...');
                    $.get('/getdatadetails',data={'dataset_uri': dataset, 'resource_uri': obj_uri},function(data)
                    {
                      $('#trgDetailsLS').html(data);
                      $("#trgDetailsLS li").on('click', function()
                      {  selectListItemUniqueWithTarget(this);
                      });
                    });
                  });

              });
          }
          else {
              var evidence_div = '#evidence_list_col';

              $('#inspect_linkset_cluster_details_col').html('');
              $('#inspect_linkset_cluster_details_col').hide();
              $('#inspect_lens_lens_details_col').html('');
              $('#inspect_lens_lens_details_col').hide();
              $('#inspect_linkset_linkset_details_col').show();

              // GEt CORRESPONDENCE DETAILS
              $('#details_list_col').html('Loading...');
              $.get('/getdetails',data=data,function(data)
              {
                  // DETAIL liST COLUMN
                  $('#details_list_col').html(data);

                  // SOURCE CLICK
                  $("#srcDatasetLI").on('click', function()
                  {
                    $('#srcDetails').html('Loading...');
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
                    $('#trgDetails').html('Loading...');
                    $.get('/getdatadetails',data={'dataset_uri': objectTarget_uri, 'resource_uri': obj_uri},function(data)
                    {
                      $('#trgDetails').html(data);
                      $("#trgDetails li").on('click', function()
                      {  selectListItemUniqueWithTarget(this);
                      });
                    });
                  });
              });
              // graph_uri = 'http://risis.eu/linkset/';
          }

          $(evidence_div).html('Loading...');
          $.get('/getevidence',data={'singleton_uri': uri, 'graph_uri': graph_uri},function(data)
          {
              $(evidence_div).html(data);
          });

      });

  });
}

function showDetailsLinksetCluster(rq_uri, graph_uri, detailsDict, filter_uri='', filter_term='')
{
  var graph_label = graph_uri;
//  var subjectTarget = detailsDict.subTarget_stripped.value;
//  var objectTarget = detailsDict.objTarget_stripped.value;
//  var subjectTarget_uri = detailsDict.subTarget.value;
//  var objectTarget_uri = detailsDict.objTarget.value;
  var graph_triples = detailsDict.triples.value;
//  var alignsSubjects = detailsDict.s_property.value;
//  var alignsObjects = detailsDict.o_property.value;
  var alignsMechanism = detailsDict.mechanism.value;
//  var operator = detailsDict.operator.value;
//  var alignsSubjectsList = detailsDict.s_property_list.value
//  var alignsObjectsList = detailsDict.o_property_list.value
//  var crossCheckSubject = detailsDict.s_crossCheck_property.value
//  var crossCheckObject = detailsDict.o_crossCheck_property.value

  hideColDiv('divInvestigation');

  div = 'creation_linkset_cluster_correspondence_col';
  graph_menu = 'linkset';

  $('#'+div).show();
  $('#'+div).html('Loading...');

  // FUNCTION THAT GETS THE LIST OF CORRESPONDENCES
  $.get('/getcorrespondences3',data={'rq_uri': rq_uri,
                                    'graph_uri': graph_uri,
                                    'filter_uri': filter_uri,
                                    'filter_term': filter_term,
                                    'label': graph_label,
                                    'graph_menu': graph_menu,
                                    'graph_triples': graph_triples,
//                                    'operator': operator,
                                    'alignsMechanism': alignsMechanism},function(data)
  {
//      console.log(data);
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
          var source = $(this).attr('source');
          var target = $(this).attr('target');
          var source_aligns = $(this).attr('source_aligns');
          var target_aligns = $(this).attr('target_aligns');

          //HANDLING THE SELECTION/DE-SELECTION OF CLICKED CORRESPONDENCES
          selectListItemUniqueWithTarget(this);

          var data = {'uri': uri, 'graph_uri': graph_uri,
                            'sub_uri': sub_uri, 'obj_uri': obj_uri,
                            'subjectTarget': source,
                            'objectTarget': target,
                            'alignsSubjects': source_aligns,
                            'alignsObjects': target_aligns,
                            'alignsSubjectsList': source_aligns,
                            'alignsObjectsList': target_aligns,
                            'crossCheckSubject': source_aligns,
                            'crossCheckObject': target_aligns
                            }

          var evidence_div = '#evidence_linkset_cluster_list_col';

          $('#inspect_linkset_linkset_details_col').html('');
          $('#inspect_linkset_linkset_details_col').hide();
          $('#inspect_lens_lens_details_col').html('');
          $('#inspect_lens_lens_details_col').hide();
          $('#inspect_linkset_cluster_details_col').show();
          $('#details_linkset_cluster_list_col').show();

          // GEt CORRESPONDENCE DETAILS
          $('#details_linkset_cluster_list_col').html('Loading...');
          $.get('/getdetails',data=data,function(data)
          {
              // DETAIL liST COLUMN
//              console.log(data)
              $('#details_linkset_cluster_list_col').html(data);

              // SOURCE CLICK
              $("#srcDatasetLI").on('click', function()
              {
                $('#srcDetails').html('Loading...');
                $.get('/getdatadetails',data={'dataset_uri': source, 'resource_uri': sub_uri},function(data)
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
                $('#trgDetails').html('Loading...');
                $.get('/getdatadetails',data={'dataset_uri': target, 'resource_uri': obj_uri},function(data)
                {
                  $('#trgDetails').html(data);
                  $("#trgDetails li").on('click', function()
                  {  selectListItemUniqueWithTarget(this);
                  });
                });
              });
          });

          $(evidence_div).html('Loading...');
          $.get('/getevidence',data={'singleton_uri': uri, 'graph_uri': graph_uri},function(data)
          {
              $(evidence_div).html(data);
          });

      });

  });
}

function validationRadioOnClick(th)
{
    var list = findAncestor(th,'evidence_col');
    var type = $(list).attr('type');
//    alert($(list).attr('type'));

    if (type == 'lens')
    {
        var srcDetails = 'srcDetailsLS'
        var trgDetails = 'trgDetailsLS'
    }
    else
    {
        var srcDetails = 'srcDetails'
        var trgDetails = 'trgDetails'
    }

    var value1 = 'x';
    var value2 = 'y';
    var pred1 = 'px';
    var pred2 = 'py';
    var dataset1 = 'dsx';
    var dataset2 = 'dsy';

   // get the selected predicate within the source div
   var selected_elems = selectedElemsInDiv(srcDetails);
   if (selected_elems.length > 0)
   { var pred_source = selected_elems[0]; //assuming only one is selected
     value1 = $(pred_source).attr('value');
     pred1 = $(pred_source).attr('label');
   }

   // get the selected predicate within the target div
   var selected_elems = selectedElemsInDiv(trgDetails);
   if (selected_elems.length > 0)
   { var pred_target = selected_elems[0]; //assuming only one is selected
     value2 = $(pred_target).attr('value');
     pred2 = $(pred_target).attr('label');
   }

     dataset1 = $('#'+srcDetails).attr('target');
     dataset2 = $('#'+trgDetails).attr('target');


    var text = ' based on the values "'
                + value1 + '" and "' + value2 + '" respectively of the properties "'
                + pred1 + '" from "' + dataset1 + '" and "'
                + pred2 + '" from "' + dataset2 + '"';

    if(document.getElementById('ValidationRefine_btn').checked) {
        text = 'I disagree with this particular alignment ' + text;
    } else if(document.getElementById('ValidationYes_btn').checked) {
        pred1 = $('#'+srcDetails).attr('aligns'); //'px0'; //SourceAligns
        pred2 = $('#'+trgDetails).attr('aligns'); //'py0'; //TargetAligns
        var text_agree = ' based on the aligned properties "'
                + pred1 + '" from "' + dataset1 + '" and "'
                + pred2 + '" from "' + dataset2 + '"';
        text = 'I agree with this particular alignment ' + text_agree;
        // TODO: fix the messages for lens
        if (type == 'lens')
            text = 'I agree with this particular alignment based on the aligned properties';
    } else if(document.getElementById('ValidationNo_btn').checked) {
        pred1 = $('#'+srcDetails).attr('aligns'); //'px0'; //SourceAligns
        pred2 = $('#'+trgDetails).attr('aligns'); //'py0'; //TargetAligns
        text = 'I agree with the general alignment of the properties "'
                + pred1 + '" from "' + dataset1 + '" and "'
                + pred2 + '" from "' + dataset2
                + '" but I disagree with this particular alignment ' + text;
    }
    else { text = '';
    }

//    alert(text);

    $('#validation_textbox').val(text);
}


function validationSaveOnClick(th)
{
  if ( !(document.getElementById('ValidationRefine_btn').checked) &&
        !(document.getElementById('ValidationYes_btn').checked) &&
        !(document.getElementById('ValidationNo_btn').checked) )
  {
    $('#evidence_message_col').html(addNote('Select one of the three options bellow.'))
  } else
  {

        var listCol = findAncestor(th,'evidence_col');
        var type = $(listCol).attr('type');
//        alert(type);

        if (type == 'lens')
        {
            var srcDetails = 'srcDetailsLS'
            var trgDetails = 'trgDetailsLS'
        }
        else
        {
            var srcDetails = 'srcDetails'
            var trgDetails = 'trgDetails'
        }

      // retrieve the uri of the selected singleton
      var lg = document.getElementById('corresp_list_group');
      var graph_uri = $(lg).attr("uri");
      var target = $(lg).attr("target");
      var elem = document.getElementById(target);
      var uri = $(elem).attr("uri");

      var research_uri = $('#creation_linkset_selected_RQ').attr('uri');
      if (!research_uri)
      {   var research_uri = $('#creation_lens_selected_RQ').attr('uri'); }

      // if the validation option selected is reject&refine
      // TODO: adpat for refinement of lens
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
               $('#creation_linkset_filter_row').hide();
               btn = document.getElementById('btn_refine_linkset');
               newSelectButton(btn);
               $('#creation_linkset_row').show();
               activateTargetDiv(targetId="refine_linkset_heading",cl="panel-heading");

                var validation_text = $('#validation_textbox').val();
                var type = 'reject';

                 // register the agreement comment as evidence
                 $.get('/updateevidence',data={'singleton_uri': uri,
                                               'type': type,
                                               'research_uri': research_uri,
                                               'validation_text': validation_text},
                                         function(data)
                 {
                    // reload the evidences
                    $('#evidence_list_col').html('Reloading...');

                    $.get('/getevidence',data={'singleton_uri': uri, 'graph_uri': graph_uri},function(data)
                    {
                          $('#evidence_list_col').html(data);
                    });
                 });

               $.get('/getlinksetdetails',data={'linkset': graph_uri,
                                             'template': 'none'},function(data)
               {
                    var obj = JSON.parse(data);
                    loadEditPanel(obj, mode='reject-refine');

                   // load the properties selected for refinement
                   setAttr('trg_selected_pred','uri',$(pred_target).attr('uri'));
                   $('#trg_selected_pred').html($(pred_target).attr('label'));
                   setAttr('src_selected_pred','uri',$(pred_source).attr('uri'));
                   $('#src_selected_pred').html($(pred_source).attr('label'));

               });

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
         {   var type_val = 'accept';
         } else
         // if the validation option selected is disagreement
         if(document.getElementById('ValidationNo_btn').checked)
         {    var type_val = 'reject';
         }

//         loadingGif(document.getElementById('evidence_message_col'), 2);
         $('#evidence_message_col').html(addNote("Inserting validation",cl='warning'))

         // register the agreement comment as evidence
         $.get('/updateevidence',data={'singleton_uri': uri,
                                       'type': type_val,
                                       'research_uri': research_uri,
                                       'validation_text': validation_text},
                                 function(data)
         {
            // reload the evidences
            $(listCol).html('Reloading...');

            $.get('/getevidence',data={'singleton_uri': uri, 'graph_uri': graph_uri},function(data)
            {
                  $(listCol).html(data);
                  $('#evidence_message_col').html(addNote("Validation inserted",cl='success'));
//                  loadingGif(document.getElementById('evidence_message_col'), 2, show=false);
            });
         });

      }
  }
}


function deleteValidationClick(th)
{

    var listCol = findAncestor(th,'evidence_col');
    var type = $(listCol).attr('type');

    if (type == 'lens')
    {
        var srcDetails = 'srcDetailsLS'
        var trgDetails = 'trgDetailsLS'
    }
    else
    {
        var srcDetails = 'srcDetails'
        var trgDetails = 'trgDetails'
    }

    // retrieve the uri of the selected singleton
    var lg = document.getElementById('corresp_list_group');
    var graph_uri = $(lg).attr("uri");
    var target = $(lg).attr("target");
    var elem = document.getElementById(target);
    var singleton_uri = $(elem).attr("uri");

    var rq_uri = $('#creation_linkset_selected_RQ').attr('uri');
    if (!rq_uri)
    {   var rq_uri = $('#creation_lens_selected_RQ').attr('uri'); }

    if (rq_uri && graph_uri && singleton_uri ) {
       // retrieve the selected properties, if any

       $.get('/deleteValidation',data={'rq_uri': rq_uri,
                                       'graph_uri': graph_uri,
                                       'singleton_uri': singleton_uri},
                                       function(data)
       {

            var obj = JSON.parse(data);

            $('#linkset_add_filter_message_col').html(addNote(obj.message,cl='warning'));

            $.get('/getevidence',data={'singleton_uri': singleton_uri, 'graph_uri': graph_uri},function(data)
            {
                  $('#evidence_list_col').html(data);
            });

       });

    }


}
