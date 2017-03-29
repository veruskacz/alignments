// function fired when the Creation Mode is selected
// by clicking #modeDropdown

function modeCreation(val)
{
   // change the name and mode of the button modeDropdown
   var y = document.getElementById('modeDropdown');
   $(y).html(val + '<span class="caret"></span>');
   y.setAttribute("mode", 'C');

   // hide investigation div
   $('#divInvestigation').hide();
   $('#investigation_buttons_col').hide();

   // "empty" and show divCreation
   hideColDiv('divCreation');
   $('#divCreation').show();

   // reset all buttons in the creation mode to primary and show
   resetButtons('creation_buttons_col');
   $('#creation_buttons_col').show();

}

///////////////////////////////////////////////////////////////////////////////
// Functions called at onclick of the main buttons in graphs.html
///////////////////////////////////////////////////////////////////////////////
function idea_button(targetId)
{
  activateTargetDiv(targetId);


}

function linkset_button(targetId)
{
   activateTargetDiv(targetId);

   // get research questions
   $.get('/getrquestions',
          data = {'template': 'list_dropdown.html',
                  'function': 'rqClick(this,"creation")'},
          function(data)
   {
     //load the results rendered as a button into a div-col
     $('#button_creation_linkset_RQ_col').html(data);
   });
}

function lens_button(targetId)
{
   activateTargetDiv(targetId);

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
              description = 'The operator UNION requires the selection of linksets or lenses that need to be unified. It means that correspondences that happen more once will be unified and allow for tracking provenace (e.g. how many times it was asserted). ';
          }
          else if (operator_label == 'intersection')
          {
              description = 'The operator INTERSECTION ...';
          }
          else if (operator_label == 'transitive')
          {
              description = 'The operator TRANSITIVE ';
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
}

function view_button(targetId)
{
 activateTargetDiv(targetId);

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

         if ((view_lens.length > 0) && (view_filter.length > 0))
         {
             var specs = {'rq_uri': rq_uri,
                          'view_lens[]': view_lens,
                          'view_filter[]': view_filter};

             $.get('/createView', specs, function(data)
             {
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
}


///////////////////////////////////////////////////////////////////////////////
// Functions called at onclick of the buttons in ideaCreation.html
///////////////////////////////////////////////////////////////////////////////

function create_idea_button(th)
{
  // ÷selectMultiButton(th);
  if (selectMultiButton(th)) {
    $('#idea_create_row').show();
    $('#inspect_idea_row').hide();
    var btn = document.getElementById('btn_inspect_idea');
    resetButton(btn);

     var rq_selected = document.getElementById('creation_idea_selected_RQ');
     rq_selected.setAttribute("uri", "");
     $('#creation_idea_selected_RQ').html("");
  }
  else {
    $('#idea_create_row').hide();
  }
}

function inspect_idea_button(th)
{
  if (selectMultiButton(th))
  {
    $('#inspect_idea_row').show();
    $('#idea_create_row').hide();
    var btn = document.getElementById('btn_create_idea');
    resetButton(btn);

     // get research questions
     $.get('/getrquestions',
            data = {'template': 'list_dropdown.html',
                    'function': 'rqClick(this,"idea")'},
            function(data)
     {
       //load the results rendered as a button into a div-col
       $('#button_idea_RQ_col').html(data);
     });


     var rq_input = document.getElementById('research_question');
     rq_input.setAttribute("uri", "");
     rq_input.value = "";

  }
  else {
    $('#inspect_idea_row').hide();
  }
}

function update_idea_enable()
{
    $('#creation_idea_selected_graphtype_list').html("");
    $('#creation_idea_update_col').show();
    $.get('/getgraphsentitytypes', data = { 'function': 'datasetMappingClick(this);'},
          function(data)
    {
       $('#creation_idea_graphtype_list').html(data);
    });
}

function datasetMappingClick(th)
{
  var target = $(th.parentNode).attr('target');
  var newContainer = document.getElementById(target);
  $(newContainer).append(th);
}

function updateIdeaClick()
{
   var elem = document.getElementById('creation_idea_selected_graphtype_list');
   var elems = elem.getElementsByClassName('list-group-item');
   var i;
   var list = []
   var dict = {}
   for (i = 0; i < elems.length; i++) {
     dict = { 'graph':$(elems[i]).attr('uri'),
              'type':$(elems[i]).attr('type_uri') }
     list.push(JSON.stringify(dict));
   }

   var rq_uri = $('#research_question').attr('uri');

   if (rq_uri == "")
   {
      rq_uri = $('#creation_idea_selected_RQ').attr('uri');
   }

   if ((rq_uri) && (list.length > 0))
   {
      $.get('/updaterq',data={'rq_uri': $(this).attr('rq_uri'), 'list[]': list},function(data)
     {

         $('#idea_update_message_col').html(data);
     });
   } else {
      $('#idea_update_message_col').html("Select a Reserach Question!");
   }
}

function createIdeaClick()
{
   var rq_input = document.getElementById('research_question');
   $.get('/insertrq',data={'question': rq_input.value},function(data)
   {
       var obj = JSON.parse(data)
      //  var rq_up_btn = document.getElementById('updateIdeaButton');
      //  rq_up_btn.setAttribute("uri", obj.rq);
      rq_input.setAttribute("uri", obj.rq);

       $('#idea_creation_message_col').html(obj.msg);

       update_idea_enable();
   });
}

///////////////////////////////////////////////////////////////////////////////
// Functions called at onclick of the buttons in linksetsCreation.html
///////////////////////////////////////////////////////////////////////////////

// Button that activates the inspect div for either inspect, refine or import modes
function inspect_linkset_activate(mode)
{
  if (mode == 'import') {
    $('#inspect_heading_panel').hide()
    $('#import_heading_panel').show()
  }
  else {
    if (mode == 'refine') {
      $('#item_identity').hide();
    }
    $('#import_heading_panel').hide()
    $('#inspect_heading_panel').show()
  }

  var rq_uri = $('#creation_linkset_selected_RQ').attr('uri');
  if (rq_uri)
  {
     $('#creation_linkset_row').hide();
     refresh_create_linkset();
     $.get('/getgraphsperrqtype',
                  data={'rq_uri': rq_uri,
                        'mode': mode,
                        'type': 'linkset',
                        'template': 'list_group.html'},
                  function(data)
     { // $('#loading2').hide();
       $('#inspect_linkset_linkset_selection_col').html(data);

       // set actions after clicking a graph in the list
       $('#inspect_linkset_linkset_selection_col a').on('click',function(e)
        {
          if (selectListItemUnique(this, 'inspect_linkset_linkset_selection_col'))
          {
            var linkset_uri = $(this).attr('uri');

            // load the panel describing the linkest
            $.get('/getlinksetdetails',data={'linkset': linkset_uri},function(data)
            { $('#inspect_linkset_linkset_details_col').html(data);
            });

            // load the panel for editing/refining linkset
            if (mode == 'refine' || mode == 'edit' || 'inspect')
            {
              enableButtons(document.getElementById('creation_linkset_buttons_col'), enable=false);
              $.get('/getlinksetdetails',data={'linkset': linkset_uri,
                                               'template': 'none'},function(data)
              {
                var obj = JSON.parse(data);

                if (mode == 'refine' || mode == 'edit')
                {
                  $('#creation_linkset_row').show();

                  setAttr('hidden_src_div','uri',obj.subTarget.value);
                  setAttr('hidden_src_div','label',obj.subTarget_stripped.value);
                  datasetClick(document.getElementById('hidden_src_div'));

                  setAttr('hidden_trg_div','uri',obj.objTarget.value);
                  setAttr('hidden_trg_div','label',obj.objTarget_stripped.value);
                  datasetClick(document.getElementById('hidden_trg_div'));

                  setAttr('src_selected_entity-type','uri',obj.s_datatype.value);
                  setAttr('src_selected_entity-type','style','background-color:lightblue');
                  $('#src_selected_entity-type').html(obj.s_datatype_stripped.value);

                  setAttr('trg_selected_entity-type','uri',obj.o_datatype.value);
                  setAttr('trg_selected_entity-type','style','background-color:lightblue');
                  $('#trg_selected_entity-type').html(obj.o_datatype_stripped.value);

                  if (mode == 'refine')
                  {
                    $('#button-src-entity-type-col').hide();
                    $('#button-trg-entity-type-col').hide();
                    $('#button-src-col').hide();
                    $('#button-trg-col').hide();
                  }
                  else if (mode == 'edit')
                  {
                    $('#button-src-entity-type-col').show();
                    $('#button-trg-entity-type-col').show();
                    $('#button-src-col').hide();
                    $('#button-trg-col').hide();
                  }

                }
                else if (mode == 'inspect')
                {
                   $('#creation_linkset_correspondence_row').show();
                   showLinksetDetails(linkset_uri, obj);
                }
                enableButtons(document.getElementById('creation_linkset_buttons_col'), enable=true);
              });

            }

          }
          else { $('#inspect_linkset_linkset_details_col').html(""); }
          e.preventDefault();
          return false;
        });
     });
  }
}

// Button that activates the linkset creation div.
// It fires the request /getdatasetsperrq and  the resulting list_dropdown are
// loaded into both buttons button-src-col and button-trg-col
// Each item in the list is settled with onclick function datasetClick(this);
function create_linkset_activate()
{
   refresh_create_linkset();
   $('#loading').show();
   $.get('/getdatasetsperrq',
          data = {'template': 'list_dropdown.html',
                  'rq_uri': $('#creation_linkset_selected_RQ').attr('uri'),
                  'function': 'datasetClick(this);'},
          function(data)
   {  // hide the loading message
      $('#loading').hide();
      $('#src_datasets_row').show();
      $('#src_entitytype_row').show();
      $('#trg_datasets_row').show();
      $('#trg_entitytype_row').show();
      // load the resultant rendered template into source and target buttons
      $('#button-src-col').html(data);
      $('#button-trg-col').html(data);
   });
}

// Button that actually creates the linkset
// it checks the selected elements and assemble them into dictionaries
// be passed as parameters to the request /createLinkset
function createLinksetClick()
{
    $('#linkset_creation_message_col').html("");

    var srcDict = {};
    if (($('#src_selected_graph').attr('uri')) &&
       ($('#src_selected_pred').attr('uri') ||
       ($('#selected_meth').attr('uri') == 'identity')) &&
       ($('#src_selected_entity-type').attr('uri'))  )
    {
       var aligns = $('#src_selected_pred').attr('uri');
       if ($('#selected_meth').attr('uri') == 'identity')
          { aligns = "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"; }

       srcDict = {'graph': $('#src_selected_graph').attr('uri'),
                  'aligns': aligns,
                  'entity_datatye': $('#src_selected_entity-type').attr('uri')};
    }

    var trgDict = {};
    if (($('#trg_selected_graph').attr('uri')) &&
        ( $('#trg_selected_pred').attr('uri') ||
         ($('#selected_meth').attr('uri') == 'embededAlignment') ||
         ($('#selected_meth').attr('uri') == 'identity')) &&
       ($('#trg_selected_entity-type').attr('uri')) )
    {
       var aligns = $('#trg_selected_pred').attr('uri');
       if ($('#selected_meth').attr('uri') == 'identity')
          { aligns = "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"; }

       trgDict = {'graph': $('#trg_selected_graph').attr('uri'),
                  'aligns': aligns,
                  'entity_datatye': $('#trg_selected_entity-type').attr('uri')};
    }

    if ((Object.keys(srcDict).length) &&
        (Object.keys(trgDict).length) &&
        ($('#selected_meth').attr('uri'))
        )
    {
        var specs = {
          'rq_uri': $('#creation_linkset_selected_RQ').attr('uri'),
          'src_graph': $('#src_selected_graph').attr('uri'),
          'src_aligns': $('#src_selected_pred').attr('uri'),
          'src_entity_datatye': $('#src_selected_entity-type').attr('uri'),

          'trg_graph': $('#trg_selected_graph').attr('uri'),
          'trg_aligns': $('#trg_selected_pred').attr('uri'),
          'trg_entity_datatye': $('#trg_selected_entity-type').attr('uri'),

          'mechanism': $('#selected_meth').attr('uri')
        }

        var message = "EXECUTING YOUR LINKSET SPECS.</br>PLEASE WAIT UNTIL THE COMPLETION OF YOUR EXECUTION";
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
}


function refineLinksetClick()
{
  $('#linkset_refine_message_col').html("");

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
      ( $('#trg_selected_pred').attr('uri') ||
       ($('#selected_meth').attr('uri') == 'embededAlignment')) &&
     ($('#trg_selected_entity-type').attr('uri')) )
  {
     trgDict = {'graph': $('#trg_selected_graph').attr('uri'),
                'aligns': $('#trg_selected_pred').attr('uri'),
                'entity_datatye': $('#trg_selected_entity-type').attr('uri')};
  }

  var linkset = '';
  var elems = selectedElemsInGroupList('inspect_linkset_linkset_selection_col');
  if (elems.length > 0) // it should have only one selected
  {
    linkset = $(elems[0]).attr('uri');
  }


  if ((Object.keys(srcDict).length) &&
      (Object.keys(trgDict).length) &&
      ($('#selected_meth').attr('uri')) &&
      (linkset))
  {
      var specs = {
        'rq_uri': $('#creation_linkset_selected_RQ').attr('uri'),
        'linkset_uri': linkset,

        'src_graph': $('#src_selected_graph').attr('uri'),
        'src_aligns': $('#src_selected_pred').attr('uri'),
        'src_entity_datatye': $('#src_selected_entity-type').attr('uri'),

        'trg_graph': $('#trg_selected_graph').attr('uri'),
        'trg_aligns': $('#trg_selected_pred').attr('uri'),
        'trg_entity_datatye': $('#trg_selected_entity-type').attr('uri'),

        'mechanism': $('#selected_meth').attr('uri')
      }

      var message = "EXECUTING YOUR LINKSET SPECS.</br>PLEASE WAIT UNTIL THE COMPLETION OF YOUR EXECUTION";
      $('#linkset_refine_message_col').html(message);

      // call function that creates the linkset
      // HERE!!!!
      $.get('/refineLinkset', specs, function(data)
      {
            var obj = JSON.parse(data);
            $('#linkset_refine_message_col').html(obj.message);
      });

  }
  else {
    $('#linkset_refine_message_col').html("Some feature is not selected!");
  }
}
///////////////////////////////////////////////////////////////////////////////
// Functions called when list-itens within buttons or groups list
///////////////////////////////////////////////////////////////////////////////

// Function fired onclick of a research question from list
// Make it reusable???
function rqClick(th, mode)
{
  // get the values of the selected rq
  var rq_uri = $(th).attr('uri');
  var rq_label = $(th).attr('label');

  if (mode == 'creation')
  {
    // show the selected rq_label
    setAttr('creation_linkset_selected_RQ','uri',rq_uri);
    $('#creation_linkset_selected_RQ').html(rq_label);

    //enable the creation button
    refresh_create_linkset();
    enableButtons(document.getElementById('creation_linkset_buttons_col'));
    enableButton('createLinksetButton');

    // get the datasets for the selected rq
    // show the creation_linkset_row with a loading message
    var btn = document.getElementById('btn_inspect_linkset');
    btn.onclick();
  }
  else if (mode == 'idea') {
    setAttr('creation_idea_selected_RQ','uri',rq_uri);
    $('#creation_idea_selected_RQ').html(rq_label);

    // set the button that will update the RQ with the mapping
    // var rq_up_btn = document.getElementById('updateIdeaButton');
    // rq_up_btn.setAttribute("uri", rq_uri);

    // loads and shows the update panel
    update_idea_enable();
  }
}

// Function fired onclick of a dataset from list. It fires the requests
// /getentitytyperq and /getpredicates the resulting list_dropdown are
// loaded into both buttons button-src-col and button-trg-col.
// Each item in the list is settled with onclick function datasetClick(this).
// It reads from the ancestor element of class 'graph-list' the
// (-) element in which to copy the chosen item through the tag 'targetTxt'
// (-) element in which to laod the resulting entity-types list through the tag 'targetBtn'
// (-) element in which to laod the resulting predicates list through the tag 'listCol'
function datasetClick(th)
{
    list = findAncestor(th,'graph-list');

    //refresh the source components of this task
    // refresh_create_linkset(mode=$(list).attr('mode'));

    // get the graph uri and label from the clicked dataset
    var graph_uri = $(th).attr('uri');
    var graph_label = $(th).attr('label');

    // Attribute the uri of the selected graph to the div
    // where the name/label is displayed
    var targetTxt = $(list).attr('targetTxt');
    setAttr(targetTxt,'uri',graph_uri);
    $('#'+targetTxt).html(graph_label.toUpperCase());
    setAttr(targetTxt,'style','background-color:lightblue');

    $.get('/getentitytyperq',
              data={'rq_uri': $('#creation_linkset_selected_RQ').attr('uri'),
                    'function': 'entityTypeClick(this);',
                    'graph_uri': graph_uri},
              function(data)
    { // load the rendered template into the target column
      var button = $(list).attr('targetBtn');
      $('#'+button).html(data);
    });

    // Exit a waiting message for the user to know loading time might be long.
    var listCol = $(list).attr('targetList');
    $('#'+listCol).html('Loading...');
    // get the distinct predicates and example values of a graph into a list group
    $.get('/getpredicates', data={'dataset_uri': graph_uri,
                                  'function': 'predicatesClick(this)'},
                            function(data)
    {  // load the rendered template into the column target list col
       $('#'+listCol).html(data);
    });
}

// Function fired onclick of a entity type from list it reads from
// the ancestor element of class 'entity-list' the element in which to
// copy the chosen item through the tag 'targetTxt'
function entityTypeClick(th)
{
    list = findAncestor(th,'entity-list');

    // get the graph uri and label from the clicked element
    var pred_uri = $(th).attr('uri');
    var pred_label = $(th).attr('label');

    // Attributes the uri of the selected predicate to the div
    // where the name is displayed
    var targetTxt = $(list).attr('targetTxt');
    setAttr(targetTxt,'uri',pred_uri);
    $('#'+targetTxt).html(pred_label);
    setAttr(targetTxt,'style','background-color:lightblue');
}

// Function fired onclick of a predicates from list it reads from
// the ancestor element of class 'pred-list' the element in which to
// copy the chosen item through the tag 'targetTxt'
function predicatesClick(th)
{
    list = findAncestor(th,'pred-list');

    // get the graph uri and label from the clicked element
    var pred_uri = $(th).attr('uri');
    var pred_label = $(th).attr('label');

    // Attributes the uri of the selected predicate to the div
    // where the name is displayed
    var targetTxt = $(list).attr('targetTxt');
    setAttr(targetTxt,'uri',pred_uri);
    $('#'+targetTxt).html(pred_label);
    setAttr(targetTxt,'style','background-color:lightblue');
}

// Function fired onclick of a methods from list
function methodClick(th)
{
    var description = '';
    var method = $(th).attr('uri');
    var meth_label = $(th).attr('label');
    if (method == 'identity')
    {
      //refresh_create_linkset(mode='pred');
      $('#src_selected_pred_row').hide();
      $('#src_list_pred_row').hide();
      $('#trg_selected_pred_row').hide();
      $('#trg_list_pred_row').hide();
      description = `The method IDENTITY aligns the identifier of the source with the identifier of the target.
                     This imples that both datasets use the same Unified Resource Identifier (URI).`;
    }
    else if (method == 'embededAlignment')
    {
      //refresh_create_linkset(mode='pred');
      $('#src_selected_pred_row').show();
      $('#src_list_pred_row').show();
      $('#trg_selected_pred_row').hide();
      $('#trg_list_pred_row').hide();
      description = `The method EMBEDED ALIGNMENT EXTRATION extracts an alignment already provided within the source dataset.
                     The extraction relies on the value of the linking property, i.e. property of the source that holds the identifier of the target. However, the real mechanism used to create the alignment (at the source) is unknown.`;
    }
    else
    {
        //refresh_create_linkset(mode='pred');
        $('#src_selected_pred_row').show();
        $('#src_list_pred_row').show();
        $('#trg_selected_pred_row').show();
        $('#trg_list_pred_row').show();
        if (method == 'exactStrSim')
        {
          description = 'The method EXACT STRING SIMILARITY is used to align the source and the target by matching the (string) values of the selected properties.';
        }
        else if (method == 'approxStrSim')
        {
          description = 'The method APPROXIMATE STRING SIMILARITY is used to align the source and the target by approximating the match of the (string) values of the selected properties according to a threshold.';
        }
        else if (method == 'geoSim')
        {
          description = 'The method GEO SIMILARITY is used to align the source and the target by detecting whether the values of the selected properties of source and target appear within the same geographical boundary.';
        }
    }

    // Attribute the label of the selected method to the div
    // where the name is displayed
    setAttr('selected_meth','uri',method);
    //setAttr('selected_meth','label',meth_label);
    $('#selected_meth').html(meth_label);
    setAttr('selected_meth','style','background-color:lightblue');
    $('#selected_method_desc').html(description);
}


///////////////////////////////////////////////////////////////////////////////
// Functions for refreshing selection elements in each div
///////////////////////////////////////////////////////////////////////////////
function refresh_create_linkset(mode='all')
{
    var elem = Object;
    $('#linkset_creation_message_col').html("");
    if (mode == 'all')
    {
      $('#button-src-entity-type-col').show();
      $('#button-trg-entity-type-col').show();
      $('#button-src-col').show();
      $('#button-trg-col').show();

      elem = document.getElementById('src_selected_graph');
      $('#src_selected_graph').html("Select a Graph");
      elem.setAttribute('uri', '');
      elem.setAttribute('style', 'background-color:none');

      elem = document.getElementById('trg_selected_graph');
      $('#trg_selected_graph').html("Select a Graph");
      elem.setAttribute('uri', '');
      elem.setAttribute('style', 'background-color:none');

      elem = document.getElementById('selected_meth');
      $('#selected_meth').html("Select a Method");
      elem.setAttribute('label', '');
      elem.setAttribute('style', 'background-color:none');
      $('#selected_method_desc').html("Method Description");


      $('#inspect_linkset_linkset_details_col').html("");
    }

    if (mode == 'all' || mode == 'source')
    {
      $('#button-src-col').html('<div id="hidden_src_div" style="display:none" uri="" label="" ></div>');

      elem = document.getElementById('src_selected_entity-type');
      $('#src_selected_entity-type').html("Select an Entity Type");
      elem.setAttribute('uri', '');
      elem.setAttribute('style', 'background-color:none');

      $('#src_predicates_col').html('');
    }

    if (mode == 'all' || mode == 'target')
    {
      $('#button-trg-col').html('<div id="hidden_trg_div" style="display:none" uri="" label="" ></div>');

      elem = document.getElementById('trg_selected_entity-type');
      $('#trg_selected_entity-type').html("Select an Entity Type");
      elem.setAttribute('uri', '');
      elem.setAttribute('style', 'background-color:none');

      $('#trg_predicates_col').html('');
    }

    if (mode == 'all' || mode == 'source' || mode == 'pred')
    {
      elem = document.getElementById('src_selected_pred');
      $('#src_selected_pred').html('Select a Property + <span style="color:blue"><strong> example value </strong></span>');
      elem.setAttribute('uri', '');
      elem.setAttribute('style', 'background-color:none');

      elem = document.getElementById('trg_selected_pred');
      $('#trg_selected_pred').html('Select a Property + <span style="color:blue"><strong> example value </strong></span>');
      elem.setAttribute('uri', '');
      elem.setAttribute('style', 'background-color:none');
    }

}

function refresh_create_lens(mode='all')
{
    var elem = Object;
    $('#lens_creation_message_col').html("");
    $('#selected_operator').html("Select a Operator");
    $('#selected_operator_desc').html("Operator Description");

}




// const Item = ({ url, title }) => '<p class="list-group-item-text">${title}</p>';
// // Then you could easily render it, even mapped from an array, like so:
//
// function test(){
// // // $('.list-items').html([
// // $('test_row').html([{ url: '/foo', title: 'Foo item' },{ url: '/bar', title: 'Bar item' }].map(Item).join(''));
// alert("1");
// $('test_row').html({ url: '/foo', title: 'Foo item' }.map(Item).join(''));
// alert("2");
// }
