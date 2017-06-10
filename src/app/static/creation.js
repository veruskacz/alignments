// function fired when the Creation Mode is selected
// by clicking #modeDropdown

missing_feature = "One or more features are missing."
loading_dataset = "Your dataset is being loaded!"
loaded_dataset = "Your dataset is loaded to the triple store!"
select_file = "<option>-- Select a file to view a sample --</option>"

function modeCreation(val)
{
   // change the name and mode of the button modeDropdown
   var y = document.getElementById('modeDropdown');
   $(y).html(val + '<span class="caret"></span>');
   y.setAttribute("mode", 'C');

   // hide investigation div
   $('#divInvestigation').hide();
   $('#investigation_buttons_col').hide();
   $('#admin_buttons_col').hide();

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
  var btn = document.getElementById('btn_inspect_idea');
  btn.onclick();

  if ($('#creation_idea_selected_RQ').attr('uri'))
   {
        elem = document.getElementById('creation_idea_selected_RQ');
        rqClick(elem, mode='idea');
   }

}

function mainButtonClick(targetId)
{
   activateTargetDiv(targetId);
   elem = document.getElementById(targetId);
   mode = $('#'+targetId).attr('mode');
   button = $('#'+targetId).attr('targetButton');
   text = $('#'+targetId).attr('targetText');

   $('#'+button).html('Loading...');
   // get research questions
   $.get('/getrquestions',
          data = {'template': 'list_dropdown.html',
                  'function': 'rqClick(this,"'+mode+'")'},
          function(data)
   {
     //load the results rendered as a button into a div-col
     $('#'+button).html(data);
   });

   if ($('#'+text).attr('uri'))
   {
        elem = document.getElementById(text);
        rqClick(elem, mode=mode);
   }
}

//datasetButtonClick
function importButtonClick(targetId)
{
   activateTargetDiv(targetId);
   elem = document.getElementById(targetId);

   // get files
   $.get('/default_dir_files', function(data)
   {
     //load the results rendered as a button into a div-col
     $('#ds_files_list').html(select_file + data.selected_list);
   });
}

///////////////////////////////////////////////////////////////////////////////
// Functions called at onclick of the buttons in ideaCreation.html
///////////////////////////////////////////////////////////////////////////////

function create_idea_button(th)
{
   $('#idea_creation_message_col').html('');
   $('#idea_update_message_col').html('');

  if (selectMultiButton(th)) {
    $('#idea_create_row').show();
    $('#inspect_idea_row').hide();
    $('#overview_idea_row').hide();
    $('#creation_idea_update_col').hide();
    var btn = document.getElementById('btn_inspect_idea');
    resetButton(btn);
    btn = document.getElementById('btn_overview_idea');
    resetButton(btn);
  }
  else {
    $('#idea_create_row').hide();
  }
}

function inspect_idea_button(th)
{
   $('#idea_creation_message_col').html('');
   $('#idea_update_message_col').html('');

  if (selectMultiButton(th))
  {
    $('#inspect_idea_row').show();
    $('#idea_create_row').hide();
    $('#overview_idea_row').hide();
    var btn = document.getElementById('btn_create_idea');
    resetButton(btn);
    btn = document.getElementById('btn_overview_idea');
    resetButton(btn);

     $('#button_idea_RQ_col').html('Loading...');
     // get research questions
     $.get('/getrquestions',
            data = {'template': 'list_dropdown.html',
                    'function': 'rqClick(this,"idea")'},
            function(data)
     {
       //load the results rendered as a button into a div-col
       $('#button_idea_RQ_col').html(data);
     });

    if ($('#creation_idea_selected_RQ').attr('uri'))
    {
        $('#creation_idea_update_col').show();
    }

     var rq_input = document.getElementById('research_question');
     rq_input.setAttribute("uri", "");
     rq_input.value = "";
  }
  else {
    $('#creation_idea_update_col').hide();
  }
}

function overview_idea_button(th)
{
  if (selectedButton(th)) {
    $('#idea_create_row').hide();
    $('#creation_idea_update_col').hide();
    $('#inspect_idea_row').show();

    if ($('#creation_idea_selected_RQ').attr('uri'))
    {
        $('#overview_idea_row').show();
    }

    var btn = document.getElementById('btn_inspect_idea');
    resetButton(btn);
    btn = document.getElementById('btn_create_idea');
    resetButton(btn);
  }
  else {
    $('#overview_idea_row').hide();
  }
//  refresh_create_idea();
}

function update_idea_enable(rq_uri)
{
   $('#creation_idea_selected_graphtype_list').html("");
   $('#creation_idea_registered_graphtype_list').html("");
   $('#creation_idea_update_col').show();
   $('#idea_update_message_col').html("");

    $('#creation_idea_graphtype_list').html('Loading...');
    $.get('/getgraphsentitytypes', data = {
                                    'rq_uri': rq_uri,
                                    'function': 'datasetMappingClick(this);'},
                                   function(data)
    {
       $('#creation_idea_graphtype_list').html(data);
    });

    $('#creation_idea_registered_graphtype_list').html('Loading...');
    $.get('/getgraphsentitytypes', data = {
                                    'rq_uri': rq_uri,
                                    'mode': 'added',
                                    'function': ''},
                                   function(data)
    {
       $('#creation_idea_registered_graphtype_list').html(data);
    });
}

function overview_idea_enable(rq_uri)
{
    $('#overview_idea_selected_RQ').val('Loading...');
    $('#overview_idea_dataset_mapping').val('Loading...');
    $('#overview_idea_alignment_mapping').val('Loading...');
    $('#overview_idea_lenses').val('Loading...');
    $('#overview_idea_views').val('Loading...');

    $('#overview_idea_row').show();
    $.get('/getoverviewrq', data = {'rq_uri': rq_uri}, function(data)
    {
       var obj = JSON.parse(data)
       $('#overview_idea_selected_RQ').val(obj.idea);
       $('#overview_idea_dataset_mapping').val(obj.dataset_mappings);
       $('#overview_idea_alignment_mapping').val(obj.alignment_mappings);
       $('#overview_idea_lenses').val(obj.lenses);
       $('#overview_idea_views').val(obj.view_dic);

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

   var rq_elem = document.getElementById('research_question');
   if ($(rq_elem).attr('uri') == '')
   {
      rq_elem = document.getElementById('creation_idea_selected_RQ');
   }

   if (($(rq_elem).attr('uri')!='') && (list.length > 0))
   {
     $.get('/updaterq',data={'rq_uri': $(rq_elem).attr('uri'), 'list[]': list},function(data)
     {
         rqClick(rq_elem, mode='idea');
         $('#idea_update_message_col').html(addNote(data,cl='info'));
     });
   } else {
      $('#idea_update_message_col').html(addNote(missing_feature));
   }
}

function createIdeaClick()
{
    // resetting html elements in other divs
    var rq_selected = document.getElementById('creation_idea_selected_RQ');
    rq_selected.setAttribute("uri", "");
    $('#creation_idea_selected_RQ').html("");
    setAttr('creation_idea_selected_RQ','style','background-color:none');
    $('#creation_idea_registered_graphtype_list').html("");
    $('#creation_idea_graphtype_list').html("");
    $('#creation_idea_selected_graphtype_list').html("");
    $('#idea_creation_message_col').html("");
    $('#idea_update_message_col').html("");
    // ... overview

   var rq_input = document.getElementById('research_question');
   if (rq_input.value)
   {
       $.get('/insertrq',data={'question': rq_input.value},function(data)
       {
           var obj = JSON.parse(data)
           rq_input.setAttribute("uri", obj.result);
           rq_input.setAttribute("label", rq_input.value);

           $('#idea_creation_message_col').html(addNote(obj.message,cl='info'));

           update_idea_enable();
       });
   } else {
      $('#idea_creation_message_col').html(addNote("Please informe the Research Question!"));
   }
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

     $('#inspect_linkset_linkset_selection_col').html('Loading...');
     $.get('/getgraphsperrqtype',
                  data={'rq_uri': rq_uri,
                        'mode': mode,
                        'type': 'linkset',
                        'template': 'list_group.html'},
                  function(data)
     {
       $('#inspect_linkset_linkset_selection_col').html(data);

       // set actions after clicking a graph in the list
       $('#inspect_linkset_linkset_selection_col a').on('click',function(e)
        {
          if (selectListItemUnique(this, 'inspect_linkset_linkset_selection_col'))
          {
            var linkset_uri = $(this).attr('uri');

            // load the panel describing the linkset sample
            $('#inspect_linkset_linkset_details_col').show();
            $('#inspect_linkset_linkset_details_col').html('Loading...');
            $.get('/getlinksetdetails',data={'linkset': linkset_uri},function(data)
            {
                $('#inspect_linkset_linkset_details_col').html(data);
            });

            get_filter(rq_uri, linkset_uri);

            $.get('/getlinksetdetails',data={'linkset': linkset_uri,
                                             'template': 'none'},function(data)
            {
                var obj = JSON.parse(data);

                if (mode == 'refine' || mode == 'edit' || mode == 'reject-refine')
                {
                   $('#creation_linkset_row').show();
                   loadEditPanel(obj, mode);
                }
                else if (mode == 'inspect')
                {
                   $('#creation_linkset_filter_row').show();
                   $('#creation_linkset_correspondence_row').show();
                   showDetails(rq_uri, linkset_uri, obj, filter_uri='none');
                }
            });

          }
          else { $('#inspect_linkset_linkset_details_col').html(""); }
          e.preventDefault();
          return false;
        });
     });
  }
}

function loadEditPanel(obj, mode)
{

    setAttr('hidden_src_div','uri',obj.subTarget.value);
    setAttr('hidden_src_div','label',obj.subTarget_stripped.value);

    setAttr('hidden_trg_div','uri',obj.objTarget.value);
    setAttr('hidden_trg_div','label',obj.objTarget_stripped.value);

    if (mode == 'refine' || mode == 'edit')
    {
        datasetClick(document.getElementById('hidden_src_div'));
        datasetClick(document.getElementById('hidden_trg_div'));
    }
    else
    {
        setAttr('src_selected_graph','uri',obj.subTarget.value);
        setAttr('src_selected_graph','style','background-color:lightblue');
        $('#src_selected_graph').html(obj.subTarget_stripped.value);
        setAttr('trg_selected_graph','uri',obj.objTarget.value);
        setAttr('trg_selected_graph','style','background-color:lightblue');
        $('#trg_selected_graph').html(obj.objTarget_stripped.value);
    }

    setAttr('src_selected_entity-type','uri',obj.s_datatype.value);
    setAttr('src_selected_entity-type','style','background-color:lightblue');
    $('#src_selected_entity-type').html(obj.s_datatype_stripped.value);

    setAttr('trg_selected_entity-type','uri',obj.o_datatype.value);
    setAttr('trg_selected_entity-type','style','background-color:lightblue');
    $('#trg_selected_entity-type').html(obj.o_datatype_stripped.value);

    if (mode == 'reject-refine')
    {
        setAttr('src_selected_pred','style','background-color:lightblue');
        setAttr('trg_selected_pred','style','background-color:lightblue');
    }

    if (mode == 'refine' || mode == 'reject-refine')
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


// Button that activates the linkset creation div.
// It fires the request /getdatasetsperrq and  the resulting list_dropdown are
// loaded into both buttons button-src-col and button-trg-col
// Each item in the list is settled with onclick function datasetClick(this);
function create_linkset_activate()
{
   refresh_create_linkset();
   //$('#loading').show();
   $('#button-src-col').html('Loading...');
   $('#button-trg-col').html('Loading...');
   $.get('/getdatasetsperrq',
          data = {'template': 'list_dropdown.html',
                  'rq_uri': $('#creation_linkset_selected_RQ').attr('uri'),
                  'function': 'datasetClick(this);'},
          function(data)
   {  // hide the loading message
      //$('#loading').hide();
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
       (  $('#src_selected_pred').attr('uri') ||
         ($('#selected_meth').attr('uri') == 'identity')) &&
       ($('#src_selected_entity-type').attr('uri'))  )
    {
       var aligns = $('#src_selected_pred').attr('uri');
       if ($('#selected_meth').attr('uri') == 'identity')
          { aligns = "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"; }

       var additional_entity_type_pred = '';
       var additional_entity_type_value = '';
       if ($('#src_selected_add_entity_type_pred').attr('uri') &&
           $('#src_selected_add_entity_type_value').attr('uri') )
          { additional_entity_type_pred = $('#src_selected_add_entity_type_pred').attr('uri');
            additional_entity_type_value = $('#src_selected_add_entity_type_value').attr('uri');
          }

       srcDict = {'graph': $('#src_selected_graph').attr('uri'),
                  'aligns': aligns,
                  'entity_datatye': $('#src_selected_entity-type').attr('uri'),
                  'additional_entity_type_pred': additional_entity_type_pred,
                  'additional_entity_type_value': additional_entity_type_value };
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

       var additional_entity_type_pred = '';
       var additional_entity_type_value = '';
       if ($('#trg_selected_add_entity_type_pred').attr('uri') &&
           $('#trg_selected_add_entity_type_value').attr('uri') )
          { additional_entity_type_pred = $('#trg_selected_add_entity_type_pred').attr('uri');
            additional_entity_type_value = $('#trg_selected_add_entity_type_value').attr('uri');
          }

       trgDict = {'graph': $('#trg_selected_graph').attr('uri'),
                  'aligns': aligns,
                  'entity_datatye': $('#trg_selected_entity-type').attr('uri'),
                  'additional_entity_type_pred': additional_entity_type_pred,
                  'additional_entity_type_value': additional_entity_type_value};
    }

    if ((Object.keys(srcDict).length) &&
        (Object.keys(trgDict).length) &&
        ($('#selected_meth').attr('uri')) &&
        ($('#selected_meth').attr('uri') != 'intermediate' ||
            $('#selected_int_dataset').attr('uri'))
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

          'mechanism': $('#selected_meth').attr('uri'),

          'intermediate_graph': $('#selected_int_dataset').attr('uri')
        }

        var message = "EXECUTING YOUR LINKSET SPECS.</br>PLEASE WAIT UNTIL THE COMPLETION OF YOUR EXECUTION";
        $('#linkset_creation_message_col').html(addNote(message,cl='warning'));
        loadingGif(document.getElementById('linkset_creation_message_col'), 2);

        // call function that creates the linkset
        // HERE!!!!
        $.get('/createLinkset', specs, function(data)
        {
              loadingGif(document.getElementById('linkset_creation_message_col'), 2, show=false);
              var obj = JSON.parse(data);
              $('#linkset_creation_message_col').html(addNote(obj.message,cl='info'));
        });
    }
    else {
      $('#linkset_creation_message_col').html(addNote(missing_feature));
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
        ($('#selected_meth').attr('uri') != 'intermediate' ||
            $('#selected_int_dataset').attr('uri'))&&
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

        'mechanism': $('#selected_meth').attr('uri'),

        'intermediate_graph': $('#selected_int_dataset').attr('uri')

      }

      var message = "EXECUTING YOUR LINKSET SPECS.</br>PLEASE WAIT UNTIL THE COMPLETION OF YOUR EXECUTION";
      $('#linkset_refine_message_col').html(addNote(message,cl='warning'));

      // call function that creates the linkset
      // HERE!!!!
      $.get('/refineLinkset', specs, function(data)
      {
            var obj = JSON.parse(data);
            $('#linkset_refine_message_col').html(addNote(obj.message,cl='info'));
      });

  }
  else {
    $('#linkset_refine_message_col').html(addNote(missing_feature));
  }
}


function importLinksetClick()
{
    var rq_uri = $('#creation_linkset_selected_RQ').attr('uri');

    var elems = selectedElemsInGroupList('inspect_linkset_linkset_selection_col');
    var i;
    var graphs = []
    for (i = 0; i < elems.length; i++) {
      graphs.push($(elems[i]).attr('uri'));
    }

    if (graphs.length > 0)
    {
        var data = {'rq_uri': rq_uri,
                    'graphs[]': graphs};

        var message = "EXECUTING IMPORT.<br/>PLEASE WAIT UNTIL THE COMPLETION OF YOUR EXECUTION";
        $('#linkset_import_message_col').html(addNote(message,cl='warning'));

        // call function that creates the linkset
        $.get('/importLinkset', data, function(data)
        {
            $('#linkset_import_message_col').html(addNote(data,cl='info'));
        });
    }
    else {
      $('#linkset_import_message_col').html(addNote(missing_feature));
    }
}


$('#linkset_filter_property').change(function() {
    $("#linkset_filter_value1").val('');
    $("#linkset_filter_value2").val('');
    document.getElementById("value1_greater").checked = false;
    document.getElementById("value1_equal").checked = false;
    document.getElementById("value2_smaller").checked = false;
    document.getElementById("value2_equal").checked = false;

    var selectedText = $(this).find("option:selected").text();
    if (selectedText == "Accept")
    {   $("#linkset_filter_value1").val('1');
        document.getElementById("value1_equal").checked = true;
    }
    else if (selectedText == "Reject")
    {   $("#linkset_filter_value2").val('1');
        document.getElementById("value2_smaller").checked = true;
    }
});


function addFilterLinksetClick()
{
    var rq_uri = $('#creation_linkset_selected_RQ').attr('uri');
    var linkset = '';
    var property = '';
    var value_1 = {};
    var value_2 = {};
    var elems = selectedElemsInGroupList('inspect_linkset_linkset_selection_col');
    if (elems.length > 0) // it should have only one selected
    {
        linkset = $(elems[0]).attr('uri');
        property = $('#linkset_filter_property').find("option:selected").text();
        var operator = '';
        if ($('#linkset_filter_value1').val())
        {
            if ($('#value1_greater').is(':checked'))
            {
                operator += $('#value1_greater').val();
            }
            if ($('#value1_equal').is(':checked'))
            {
                operator += $('#value1_equal').val();
            }
            if (operator)
            {
                value_1 = {'value': $('#linkset_filter_value1').val(),
                           'operator': operator }
            }
        }
        operator = '';
        if ($('#linkset_filter_value2').val())
        {
            if ($('#value2_smaller').is(':checked'))
            {
                operator += $('#value2_smaller').val();
            }
            if ($('#value2_equal').is(':checked'))
            {
                operator += $('#value2_equal').val();
            }
            if (operator)
            {
                value_2 = {'value': $('#linkset_filter_value2').val(),
                           'operator': operator }
            }
        }
    }
    if ((rq_uri != '') && (linkset != '') && (property!='--Select a Property--') &&
        ((value_1 != {}) || (value_2 != {})) )
    {
        $.get('/setlinkesetfilter',
                  data={'rq_uri': rq_uri,
                        'linkset_uri': linkset,
                        'property': property,
                        'value_1': JSON.stringify(value_1),
                        'value_2': JSON.stringify(value_2)},
                  function(data)
        {
            get_filter(rq_uri, linkset);
        });
    }
}


function applyFilterLinksetClick()
{
    var rq_uri = $('#creation_linkset_selected_RQ').attr('uri');
    var linkset_uri = ''
    var elems = selectedElemsInDiv("inspect_linkset_linkset_selection_col");
       if (elems.length > 0)
       {    linkset_uri = $(elems[0]).attr('uri');
       }

    $.get('/getlinksetdetails',data={'linkset': linkset_uri,
                                       'template': 'none'},function(data)
    {
       var obj = JSON.parse(data);

       $('#creation_linkset_filter_row').show();
       $('#creation_linkset_correspondence_row').show();
       var filter_uri = '';
       elems = selectedElemsInDiv("linkset_filter_col");
       if (elems.length > 0)
       {    filter_uri = $(elems[0]).attr('uri');
       }
       var filter_term =  $('#linkset_filter_text').val();
       if (filter_term == "-- Type a term for search & filter --")
            { filter_term = ''; }
       showDetails(rq_uri, linkset_uri, obj, filter_uri, filter_term);
    });
}


function get_filter(rq_uri, linkset)
{
    $.get('/getfilters',data={'rq_uri': rq_uri, 'graph_uri': linkset},function(data)
    {
        $('#linkset_filter_list').html(data);

        var item = '<li class="list-group-item list-group-item-warning" uri="none" id="no_filter_linkset" '
                            + '"><span class="list-group-item-heading"> None </span></li>';
        $('#linkset_filter_list').prepend(item);

        $('#linkset_filter_list li').on('click',function()
        {   selectListItemUnique(this, 'linkset_filter_list')
            //selectListItem(this);
        });

    });
}

///////////////////////////////////////////////////////////////////////////////
// Functions called at onclick of the buttons in lensCreation.html
///////////////////////////////////////////////////////////////////////////////

function inspect_lens_activate(mode)
{
  var rq_uri = $('#creation_lens_selected_RQ').attr('uri');

  $('#creation_lens_correspondence_row').hide();
  $('#creation_lens_correspondence_col').html('');
  $('#inspect_lens_lens_details_col').html('');
  refresh_create_lens();

  if (rq_uri)
  {

    $('#inspect_lens_lens_selection_col').html('Loading...');
    $.get('/getgraphsperrqtype',
                  data={'rq_uri': rq_uri,
                        'mode': mode,
                        'type': 'lens',
                        'template': 'list_group.html'},
                  function(data)
    {
      $('#inspect_lens_lens_selection_col').html(data);

      // set actions after clicking a graph in the list
      $('#inspect_lens_lens_selection_col a').on('click',function()
       {
          if (selectListItemUnique(this, 'inspect_lens_lens_selection_col'))
          {
            var lens_uri = $(this).attr('uri');

            // load the panel describing the lens
             $('#inspect_lens_lens_details_col').html('Loading...');
             $.get('getlensspecs',data={'lens': lens_uri},function(data)
             { $('#inspect_lens_lens_details_col').html(data);
             });

            // load the panel for filter
              $('#creation_lens_filter_row').show();

            // load the panel for correspondences details
              $('#creation_lens_correspondence_row').show();
              //already has Loading...
              $.get('/getlensdetails',data={'lens': lens_uri,
                                            'template': 'none'},function(data)
              {
                var obj = JSON.parse(data);
                showDetails(rq_uri, lens_uri, obj);
              });
          }
        });
    });
  }
}

function create_lens_activate()
{
   var rq_uri = $('#creation_lens_selected_RQ').attr('uri');

    //   $('#lens_creation_message_col').html('');
    refresh_create_lens();

   $('#creation_lens_linkset_selection_col').html('Loading...');
   $.get('/getgraphsperrqtype',data={'rq_uri': rq_uri,
                          'type': 'linkset',
                          'template': 'list_group.html'},function(data)
   {
     $('#creation_lens_linkset_selection_col').html(data);

     // set actions after clicking a graph in the list
     $('#creation_lens_linkset_selection_col a').on('click',function()
      { selectListItem(this); });
   });

   $('#creation_lens_lens_selection_col').html('Loading...');
   $.get('/getgraphsperrqtype',data={'rq_uri': rq_uri,
                          'type': 'lens',
                          'template': 'list_group.html'},function(data)
   {
     $('#creation_lens_lens_selection_col').html(data);

     // set actions after clicking a graph in the list
     $('#creation_lens_lens_selection_col a').on('click',function()
      { selectListItem(this); });
   });
}

function operatorClick(th)
{
  var operator_label = $(th).attr('label');

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
  else if (operator_label == 'difference')
  {
      description = 'The operator DIFFERENCE evaluates alignments as its arguments, then calculates correspondences that exists in the left-hand side but not in the right-hand side.';
  }
  $('#selected_operator_desc').html(description);
}

function createLensClick()
{
    var rq_uri = $('#creation_lens_selected_RQ').attr('uri');

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
        $('#lens_creation_message_col').html(addNote(message,cl='warning'));

        // call function that creates the linkset
        $.get('/createLens', specs, function(data)
        {
            var obj = JSON.parse(data);
            $('#lens_creation_message_col').html(addNote(obj.message, cl='info'));

            $('#creation_lens_lens_selection_col').html('Loading...');
               $.get('/getgraphsperrqtype',data={'rq_uri': rq_uri,
                                      'type': 'lens',
                                      'template': 'list_group.html'},function(data)
               {
                 $('#creation_lens_lens_selection_col').html(data);

                 // set actions after clicking a graph in the list
                 $('#creation_lens_lens_selection_col a').on('click',function()
                  { selectListItem(this); });
               });
        });
    }
    else {
      $('#lens_creation_message_col').html(addNote(missing_feature));
    }
 }

function importLensClick()
{
    var rq_uri = $('#creation_lens_selected_RQ').attr('uri');

    var elems = selectedElemsInGroupList('inspect_lens_lens_selection_col');
    var i;
    var graphs = []
    for (i = 0; i < elems.length; i++) {
      graphs.push($(elems[i]).attr('uri'));
    }
    if (graphs.length > 0)
    {
        var data = {'rq_uri': rq_uri,
                    'graphs[]': graphs};

        var message = "EXECUTING IMPORT.<br/>PLEASE WAIT UNTIL THE COMPLETION OF YOUR EXECUTION";
        $('#lens_import_message_col').html(message);

        // call function that creates the linkset
        $.get('/importLens', data, function(data)
        {
            $('#lens_import_message_col').html(addNote(data, cl='info'));
        });
    }
    else {
      $('#lens_import_message_col').html(addNote(missing_feature));
    }
}


///////////////////////////////////////////////////////////////////////////////
// Functions called at onclick of the buttons in viewsCreation.html
///////////////////////////////////////////////////////////////////////////////

function create_views_activate()
{
    var rq_uri = $('#creation_view_selected_RQ').attr('uri');
    $('#creation_view_predicates_col').html('');
    $('#creation_view_selected_predicates_group').html('');
    $('#view_creation_message_col').html('');
    $('#view_creation_save_message_col').html('');
    $('#creation_view_results_row').hide();

     $('#creation_view_dataset_col').html('Loading...');
     $.get('/getdatasetsperrq',data={'rq_uri': rq_uri,
                            'template': 'list_group.html'},function(data)
     {
       $('#creation_view_dataset_col').html(data);

       // set actions after clicking a graph in the list
       $('#creation_view_dataset_col a').on('click',function()
       {
          var graph_uri = $(this).attr('uri');
          var graph_label = $(this).attr('label');

          if (selectListItemUnique(this, 'creation_view_dataset_col'))
          {
              // Exhibit a waiting message for the user to know loading time might be long.
              $('#creation_view_predicates_col').html('Loading...');
              // get the distinct predicates and example values of a graph into a list group
              $.get('/getpredicates',data={'dataset_uri': graph_uri},function(data)
              {
                   // load the rendered template into the column #creation_view_predicates_col
                  $('#creation_view_predicates_col').html(data);

                  // set actions after clicking one of the predicates
                  $('#creation_view_predicates_col li').on('click',function()
                  {
                    var pred_uri = $(this).attr('uri');
                    var pred_label = $(this).attr('label');

                    var i;
                    var check = false;
                    var elem = document.getElementById('creation_view_selected_predicates_group');
                    if (elem) {
                        var elems = elem.getElementsByClassName('list-group-item');
                        for (i = 0; i < elems.length; i++) {
                            if ( ($(elems[i]).attr('pred_uri') == pred_uri)
                                     && ($(elems[i]).attr('graph_uri') == graph_uri) )
                            { //('true');
                              check = true;
                              break;
                            }
                        }
                        if (!check) {
                           var item = '<li class="list-group-item" pred_uri="' + pred_uri
                                    + '" graph_uri="' + graph_uri
                                    + '"><span class="list-group-item-heading"><b>'
                                    + graph_label + '</b>: ' + pred_label + '</span></li>';
                           $('#creation_view_selected_predicates_group').prepend(item);
                        }
                    }

                    $('#creation_view_selected_predicates_group li').on('ondblclick',function()
                    {
                        var id = $(this).attr('id');
                        var element = document.getElementById(id);
                        element.parentNode.removeChild(element);
                    });

                  });
              });
          }

       });
     });

     $('#creation_view_linkset_col').html('Loading...');
     $.get('/getgraphsperrqtype',data={'rq_uri': rq_uri,
                            'type': 'linkset',
                            'template': 'list_group.html'},function(data)
     {
       $('#creation_view_linkset_col').html(data);

       // set actions after clicking a graph in the list
       $('#creation_view_linkset_col a').on('click',function()
       {
          var uri = $(this).attr('uri');
          selectListItem(this);
       });
      });

     $('#creation_view_lens_col').html('Loading...');
     $.get('/getgraphsperrqtype',data={'rq_uri': rq_uri,
                            'type': 'lens',
                            'template': 'list_group.html'},function(data)
     {
       $('#creation_view_lens_col').html(data);

       // set actions after clicking a graph in the list
       $('#creation_view_lens_col a').on('click',function()
       {
          var uri = $(this).attr('uri');
          selectListItem(this);
        });
     });

}

function inspect_views_activate(mode="inspect")
{
  var rq_uri = $('#creation_view_selected_RQ').attr('uri');

  if (rq_uri)
  {
    $('#inspect_views_details_col').html('');
    $('#inspect_views_selection_col').html('Loading...');
    $.get('/getgraphsperrqtype',
                  data={'rq_uri': rq_uri,
                        'type': 'view',
                        'template': 'list_group.html'},
                  function(data)
    {
      $('#inspect_views_selection_col').html(data);

      // set actions after clicking a graph in the list
      $('#inspect_views_selection_col a').on('click',function()
       {
          if (selectListItemUnique(this, 'inspect_views_selection_col'))
          {
            $('#view_creation_message_col').html("");
            $('#view_creation_save_message_col').html("");
            $('#creation_view_selected_predicates_group').html("");
            var view_uri = $(this).attr('uri');

            //show the creation-panels containing the linksets/lenses
            //and the datasets and properties to be selected
            create_views_activate();
            $('#creation_view_row').show();
            $('#creation_view_filter_row').show();


            // load the panel for correspondences details
              $('#inspect_views_details_col').html('Loading...');
              $.get('/getviewdetails',data={'rq_uri': rq_uri,
                                            'view_uri': view_uri},function(data)
              {

                var obj = JSON.parse(data);

                $('#inspect_views_details_col').html(obj.details);

                // assigning the selected graphs and properties
                var i, elem, elems;
                elem = document.getElementById('creation_view_linkset_col');
                if (elem) {
                    elems = elem.getElementsByClassName('list-group-item');
                    for (i = 0; i < elems.length; i++) {
                        uri = $(elems[i]).attr('uri');
                        if (obj.view_lens.includes(uri))
                        {
                            selectListItem(elems[i]);
                        }
                    }
                }

                elem = document.getElementById('creation_view_lens_col');
                if (elem) {
                    elems = elem.getElementsByClassName('list-group-item');
                    for (i = 0; i < elems.length; i++) {
                        uri = $(elems[i]).attr('uri');
                        if (obj.view_lens.includes(uri))
                        {
                            selectListItem(elems[i]);
                        }
                    }
                }

                $('#creation_view_registered_predicates_group').html("");
                var view_filters = obj.view_filter_matrix
                for (i = 1; i < view_filters.length; i++) {
                      var item = '<li class="list-group-item" style="background-color:lightblue"'
                                + 'pred_uri="' + view_filters[i][1]
                                + '" graph_uri="' + view_filters[i][0]
                                + '"><span class="list-group-item-heading"><b>'
                                + view_filters[i][2] + '</b>: ' + view_filters[i][3] + '</span></li>';

                      $('#creation_view_selected_predicates_group').prepend(item);
                }

              });
//           var btn = document.getElementById('createViewButton');
//           resetButton(btn);
//           create_views_activate();
           $('#creation_view_results_row').hide();

           $("#collapse_view_lens").collapse("hide");
           $("#collapse_view_filter").collapse("hide");

          }
        });
    });

  }
}

function createViewClick(mode)
{
    $('#view_creation_message_col').html("");
    $('#view_creation_save_message_col').html("");
    var rq_uri = $('#creation_view_selected_RQ').attr('uri');
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
     var specs = {'mode': mode,
                  'rq_uri': rq_uri,
                  'view_lens[]': view_lens,
                  'view_filter[]': view_filter};

     $.get('/createView', specs, function(data)
     {
         var obj = JSON.parse(data);
         //{"metadata": metadata, "query": '', "table": []}
         $('#queryView').val(obj.query);
         if (mode=='check')
         { $('#view_creation_message_col').html(addNote(obj.metadata.message,cl='info'));
         }
         else
         { $('#view_creation_save_message_col').html(addNote(obj.metadata.message,cl='info'));
         }
         $('#creation_view_results_row').show();
         runViewClick();
     });
    }
    else {
    $('#view_creation_message_col').html(addNote(missing_feature));
    }
}

function runViewClick()
{
  //$('#view_creation_message_col').html("");
  var query = $('#queryView').val();
  $.get('/sparql',data={'query': query}, function(data)
  {
    $('#views-results').html(data);
  });
}

function showQuery(th)
{
    if (selectMultiButton(th)) {
        $('#view_query_row').show();
    }
    else {
        $('#view_query_row').hide();
    }
}

function detailsViewClick(th)
{
    if (selectMultiButton(th)) {
        $('#creation_view_row').show();
    }
    else {
        $('#creation_view_row').hide();
    }
}

function resultViewClick(th)
{
     if (selectMultiButton(th)) {
        $('#creation_view_results_row').show();
        createViewClick(mode="check");
    }
    else {
        $('#creation_view_results_row').hide();
    }
}

///////////////////////////////////////////////////////////////////////////////
// Functions called when list-itens within buttons or groups list are clicked
///////////////////////////////////////////////////////////////////////////////

// Function fired onclick of a research question from list
// Make it reusable???
function rqClick(th, mode)
{
  // get the values of the selected rq
  var rq_uri = $(th).attr('uri');
  var rq_label = $(th).attr('label');

  switch (mode) {
      case 'linkset':
          enableButtons(document.getElementById('creation_linkset_buttons_col'));

          // get the datasets for the selected rq
          // show the creation_linkset_row with a loading message
          var btn = document.getElementById('btn_inspect_linkset');

          break;
      case 'lens':
          enableButtons(document.getElementById('creation_lens_buttons_col'));

          // get the datasets for the selected rq
          // show the creation_linkset_row with a loading message
          var btn = document.getElementById('btn_inspect_lens');
          break;
      case 'idea':
          var btn = document.getElementById('btn_inspect_idea');
          update_idea_enable(rq_uri);
          overview_idea_enable(rq_uri);
          if ( selectedButton(btn) )
          { $('#overview_idea_row').hide();
          } else
          { $('#creation_idea_update_col').hide();
          }
          btn = null;
          break;
      case 'view':
          enableButtons(document.getElementById('creation_views_buttons_col'));
          refresh_create_view();
          var btn = document.getElementById('btn_inspect_view');
          break;
  }

  //set target div with selected RQ
  var target = 'creation_linkset_selected_RQ';
  setAttr(target,'uri',rq_uri);
  setAttr(target,'label',rq_label);
  setAttr(target,'style','background-color:lightblue');
  $('#'+target).html(rq_label);

  target = 'creation_lens_selected_RQ';
  setAttr(target,'uri',rq_uri);
  setAttr(target,'label',rq_label);
  setAttr(target,'style','background-color:lightblue');
  $('#'+target).html(rq_label);

  target = 'creation_view_selected_RQ';
  setAttr(target,'uri',rq_uri);
  setAttr(target,'label',rq_label);
  setAttr(target,'style','background-color:lightblue');
  $('#'+target).html(rq_label);

  target = 'creation_idea_selected_RQ';
  setAttr(target,'uri',rq_uri);
  setAttr(target,'label',rq_label);
  setAttr(target,'style','background-color:lightblue');
  $('#'+target).html(rq_label);

  if (btn)  //inital button selected
  {  btn.onclick();
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
    //alert(list);

    //refresh the source components of this task
    // refresh_create_linkset(mode=$(list).attr('mode'));

    // get the graph uri and label from the clicked dataset
    var graph_uri = $(th).attr('uri');
    var graph_label = $(th).attr('label');

    // Attribute the uri of the selected graph to the div
    // where the name/label is displayed
    var targetTxt = $(list).attr('targetTxt');
    //alert(targetTxt);
    setAttr(targetTxt,'uri',graph_uri);
    $('#'+targetTxt).html(graph_label.toUpperCase());
    setAttr(targetTxt,'style','background-color:lightblue');

    var button = $(list).attr('targetBtn');
    if (button)
    {
        // clean previously selected entity type
        targetTxt = $('#'+button).attr('targetTxt');
        setAttr(targetTxt,'uri','');
        $('#'+targetTxt).html('Select an Entity Type');
        setAttr(targetTxt,'style','background-color:none');

        // get new entity types
        $('#'+button).html('Loading...');
        $.get('/getentitytyperq',
                  data={'rq_uri': $('#creation_linkset_selected_RQ').attr('uri'),
                        'function': 'selectionClick(this, "entity-list");',
                        'graph_uri': graph_uri},
                  function(data)
        { // load the rendered template into the target column
          $('#'+button).html(data);
        });
    }


    // Load additional entity types into the div informed as targetBtn
    var button2 = $(list).attr('targetAddBtn');
    if (button2)
    {
        // clean previously selected entity type
        targetTxt = $('#'+button2).attr('targetTxt');
        setAttr(targetTxt,'uri','');
        $('#'+targetTxt).html('Select a Type-Property');
        setAttr(targetTxt,'style','background-color:none');

        // get additional entity types
        $('#'+button2).html('Loading...');
        $.get('/getpredicateslist',
                  data={'graph_uri': graph_uri,
                        'function': 'selectionClick(this, "selection-list");'},
                  function(data)
        { // load the rendered template into the target column
          $('#'+button2).html(data);
        });
    }

    var listCol = $(list).attr('targetList');
    if (listCol)
    {
        // clean previously selected entity type
        targetTxt = $('#'+listCol).attr('targetTxt');
        setAttr(targetTxt,'uri','');
        $('#'+targetTxt).html('Select a Property + <span style="color:blue"><strong> example value </strong></span>');
        setAttr(targetTxt,'style','background-color:none');

        // get the distinct predicates and example values of a graph into a list group
        $('#'+listCol).html('Loading...');
        $.get('/getpredicates', data={'dataset_uri': graph_uri,
                                      'function': 'selectionClick(this, "pred-list");'},
                                function(data)
        {  // load the rendered template into the column target list col
           $('#'+listCol).html(data);
        });
    }
}

// Function fired onclick of a option from a list
// it reads from the ancestor-element of a certain class
// the element in which to copy the chosen item through the tag 'targetTxt'
function selectionClick(th, ancestorType)
{
    list = findAncestor(th, ancestorType);

    // Attributes the uri of the selected predicate to the div
    // where the name is displayed
    var targetTxt = $(list).attr('targetTxt');
    setAttr(targetTxt,'uri', $(th).attr('uri') );
    $('#'+targetTxt).html( $(th).attr('label') );
    setAttr(targetTxt,'style','background-color:lightblue');

    //If there is a button to be loaded...
    //TODO: make it generic
    var button = $(list).attr('targetBtn');
    if (button)
    {
        // clean previously selected entity type
        targetTxt = $('#'+button).attr('targetTxt');
        setAttr(targetTxt,'uri','');
        $('#'+targetTxt).html('Select an Entity Type');
        setAttr(targetTxt,'style','background-color:none');

        // get new entity types
        var mode = $('#'+button).attr('mode');
        if (mode == 'source')
        { graph_uri = $('#src_selected_graph').attr('uri') }
        else
        { graph_uri = $('#trg_selected_graph').attr('uri') }
        $('#'+button).html('Loading...');
        $.get('/getdatasetpredicatevalues',
                  data={'graph_uri': graph_uri,
                        'predicate_uri': $(th).attr('uri') ,
                        'function': 'selectionClick(this, "selection-list");'},
                  function(data)
        { // load the rendered template into the target column
          $('#'+button).html(data);
        });
    }
}


// Function fired onclick of a methods from list
function methodClick(th)
{
    var description = '';
    var method = $(th).attr('uri');
    var meth_label = $(th).attr('label');
    $('#int_dataset_row').hide();
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
    else if (method == 'loadLinkset')
    {
      //refresh_create_linkset(mode='pred');
      $('#src_selected_pred_row').show();
      $('#src_list_pred_row').show();
      $('#trg_selected_pred_row').hide();
      $('#trg_list_pred_row').hide();
      $('#dropbox_linkset_row').show();
      description = `The method `+ '"' +`LOADS EXISTING LINKSET`+ '"' +` load the alignment provided within an RDF
                    file and convert it according to the Lenticular Lens model. Source and target datasets,
                    as well as Entity Type are mandatory. Other metadata can be filled in for documentation purpose.`;

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
        else if (method == 'intermediate')
        {
          description = 'The method MATCH VIA INTERMEDIATE DATASET is used to align the source and the target by using properties that present different descriptions of a same entity, such as country name and country code. This is possible by providing an intermediate dataset that binds the two alternative descriptions to the very same identifier.';
          $('#int_dataset_row').show();
          $('#button_int_dataset').html('Loading...');
          $.get('/getdatasets',
                  data={'template': 'list_dropdown.html',
                        'function': 'datasetClick(this);'},
                  function(data)
          {
                $('#button_int_dataset').html(data);
          });

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
    $('#linkset_import_message_col').html("");
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
      $('#creation_linkset_filter_row').hide();
      $('#creation_linkset_correspondence_row').hide();
      $('#creation_linkset_correspondence_col').html('');

      $('#int_dataset_row').hide();
      elem = document.getElementById('selected_int_dataset');
      elem.setAttribute('uri', '');
      elem.setAttribute('style', 'background-color:none');
      $('#selected_int_dataset').html("Select a Dataset");

      $('#linkset_refine_message_col').html('');
    }

    if (mode == 'all' || mode == 'source')
    {
      $('#button-src-col').html('<div id="hidden_src_div" style="display:none" uri="" label="" ></div>');

      elem = document.getElementById('src_selected_entity-type');
      $(elem).html("Select an Entity Type");
      elem.setAttribute('uri', '');
      elem.setAttribute('style', 'background-color:none');

      elem = document.getElementById('src_selected_add_entity_type_pred');
      $(elem).html("Select a Type-Property");
      elem.setAttribute('uri', '');
      elem.setAttribute('style', 'background-color:none');

      elem = document.getElementById('src_selected_add_entity_type_value');
      $(elem).html("Select a Type-Value");
      elem.setAttribute('uri', '');
      elem.setAttribute('style', 'background-color:none');

      $('#src_predicates_col').html('');
    }

    if (mode == 'all' || mode == 'target')
    {
      $('#button-trg-col').html('<div id="hidden_trg_div" style="display:none" uri="" label="" ></div>');

      elem = document.getElementById('trg_selected_entity-type');
      $(elem).html("Select an Entity Type");
      elem.setAttribute('uri', '');
      elem.setAttribute('style', 'background-color:none');

      elem = document.getElementById('trg_selected_add_entity_type_pred');
      $(elem).html("Select a Type-Property");
      elem.setAttribute('uri', '');
      elem.setAttribute('style', 'background-color:none');

      elem = document.getElementById('trg_selected_add_entity_type_value');
      $(elem).html("Select a Type-Value");
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
    $('#lens_import_message_col').html("");
    $('#lens_add_filter_message_col').html("");
    $('#lens_add_filter_message_col').html("");
    $('#selected_operator').html("Select a Operator");
    $('#selected_operator_desc').html("Operator Description");
//    $('#creation_linkset_correspondence_row').hide();
//    $('#creation_linkset_correspondence_col').html('');
    $('#creation_lens_correspondence_row').hide();
    $('#creation_lens_correspondence_col').html('');
    $('#inspect_lens_lens_details_col').html('');
}


function refresh_create_idea()
{
    $('#creation_idea_registered_graphtype_list').html("");
    $('#creation_idea_graphtype_list').html("");
}


function refresh_create_view()
{
//    alert('here');
    var btn = document.getElementById('detailsViewButton');
    resetButton(btn);
    btn = document.getElementById('createViewButton');
    resetButton(btn);
    $('#view_creation_message_col').html("");
    $('#view_creation_save_message_col').html("");
    $('#inspect_views_details_col').html("");
    $('#creation_view_linkset_col').html("");
    $('#creation_view_lens_col').html("");
    $('#creation_view_selected_predicates_group').html("");
    $('#views-results').html("");
    $('#queryView').val("");
}

function refresh_import()
{
    $('#dropbox').html('<span class="message"><strong><font size="6">Drop here your files to upload.</font></strong></span>');
    $('#upload_sample').val('NO DATASET FILE SELECTED');
    $('#ds_files_list').html(select_file);
    $('#dataset_upload_message_col').html('');
    $('#dataset_upload_message_col').html('');
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




///////////////////////////////////////////////////////////////////////////////
// Functions called at onclick of the buttons in datasetCreation.html
// (which stand now for import both dataset and alignment)
///////////////////////////////////////////////////////////////////////////////
function import_dataset_button(th)
{
    $('#import_title').html('<h3>Dataset</h3>');
    $('#import_dataset_div').show();
    $('#import_alignment_div').hide();
    refresh_import();
}

function import_alignent_button(th)
{
    $('#import_title').html('<h3>Alignment</h3>');
    $('#import_alignment_div').show();
    $('#import_dataset_div').hide();
    refresh_import();
}

$(".collapse").on('hidden.bs.collapse', function(){
    var target = document.getElementById($(this).attr('target'));
    if (target)
    {$(target).html(' <span class="badge alert-info"><strong>+</strong></span> ');}
    target = document.getElementById($(this).attr('target2'));
    if (target)
    {$(target).html(' <span class="badge alert-info"><strong>+</strong></span> ');}
    target = document.getElementById($(this).attr('target3'));
    if (target)
    {$(target).html(' <span class="badge alert-info"><strong>+</strong></span> ');}
});

$(".collapse").on('shown.bs.collapse', function(){
    var target = document.getElementById($(this).attr('target'));
    if (target)
    {$(target).html(' <span class="badge alert-info"><strong>-</strong></span> ');}
    target = document.getElementById($(this).attr('target2'));
    if (target)
    {$(target).html(' <span class="badge alert-info"><strong>-</strong></span> ');}
    target = document.getElementById($(this).attr('target3'));
    if (target)
    {$(target).html(' <span class="badge alert-info"><strong>-</strong></span> ');}
});

function convertDatasetClick()
{
    var files = getSelectValues(document.getElementById('ds_files_list'));

    //var input = document.getElementById('dataset_file_path');
    var separator = document.getElementById('ds_separator');
    var dataset = document.getElementById('ds_name');
    var entity_type = document.getElementById('ds_entity_type_name');

    if ((files.length > 0) && (dataset.value) && (entity_type.value) )
    {
        var indexes_1 = []
        indexes_1 = getSelectIndexes(document.getElementById('ds_type_list'));
        if (indexes_1.length != 0)
        {
            var rdftype = indexes_1;
        }
        else
        {
            var rdftype = [];
        }

        // not empty and not "-- Select --"
        indexes_2 = getSelectIndexes(document.getElementById('ds_subject_id'));
        if (indexes_2 != [] && indexes_2[0] != 0)
        {
            var subject_id = indexes_2[0]-1;
        }
        else
        {
            var subject_id = null;
        }

//        alert("Subject ID: " + subject_id + " | Types" + rdftype);

        $('#dataset_convertion_message_col').html(addNote("Your file is being converted!",cl='warning'));

        $.get('/convertCSVToRDF',
              data={'file': files[0],
                    'separator': separator.value,
                    'database': dataset.value,
                    'entity_type': entity_type.value,
                    'rdftype[]': rdftype,
                    'subject_id': subject_id},
              function(data)
        {
//            alert(data);
            var obj = data
//            console.log(obj);
            if (Object.keys(obj).length)
            {
                //$('#button_int_dataset').html(data);
    //            $('#dataset_convertion_message_col').html("");
                $('#dataset_convertion_message_col').html(addNote("You can now load your data to the RISIS triple store in the next panel!",cl='success'));
                enableButton('createDatasetButton');
                enableButton('schemaDatasetButton');
                enableButton('converted_sampleDatasetButton');
                setAttr('createDatasetButton','batchFile',obj.batch);
                setAttr('schemaDatasetButton','file',obj.schema);
                setAttr('converted_sampleDatasetButton','file',obj.data);
            }
            else
            {
                $('#dataset_convertion_message_col').html(addNote("Something went wrong!"));
            }
        });
    }
    else
    {
        $('#dataset_convertion_message_col').html(addNote(missing_feature));
//        if (!dataset.value)
//        { setAttr('ds_name','style','background-color:lightred'); }
//        if (!entity_type.value)
//        { setAttr('ds_entity_type_name','style','background-color:lightred'); }
    }
}


function viewSampleFileClick()
{
//    var input = document.getElementById('dataset_file_path');

    var files = getSelectValues(document.getElementById('ds_files_list'));

    if (files.length > 0)
    {
        $.get('/viewSampleFile',
              data={'file':  files[0]}, //input.value},
              function(data)
        {
            var obj = JSON.parse(data);
            $('#upload_sample').val(obj.sample);
            $('#dataset_header').val(obj.header);
            $('#dataset_upload_message_col').html(addNote("You can now convert the data!</br>Please fill in the separator in the panel below!",cl='success'));
        });
    }
    else
    {
        $('#dataset_upload_message_col').html(addNote(missing_feature));
    }
}

function viewSampleRDFFile(th)
{
//    var input = document.getElementById('dataset_file_path');
    var target_message = $(th).attr('target_message')
    var target_result = $(th).attr('target_result')
    var file = $(th).attr('file')
//    alert(target_message)
//    alert(target_result)
//    alert(file)

    if (target_message && target_result && file)
    {
        $.get('/viewSampleRDFFile',
              data={'file':  file}, //input.value},
              function(data)
        {
            var obj = JSON.parse(data);
//            console.log(obj);
            $('#'+target_result).val(obj);
            $('#'+target_message).html(addNote("A sample of the converted file is displayed in the box below",cl='success'));
        });
    }
    else if (target_message)
    {
        $('#'+target_message).html(addNote(missing_feature));
    }
}

//$('#ds_separator').onkeyup(function() {
function getHeaderColumns() {
    //alert('keyup')
    if ( document.getElementById("ds_separator").value )
    {
        var input = document.getElementById('dataset_header');
        var separator = document.getElementById('ds_separator');
        $.get('/headerExtractor',
          data={'header_line': input.value,
                'separator': separator.value},
          function(data)
        {
            $('#ds_subject_id').html("<option>-- Select --</option>"+data);
            $('#ds_type_list').html(data);

        });
        enableButton('convertDatasetButton');

    }
    else
    {
        enableButton('convertDatasetButton',enable=false);
        $('#ds_subject_id').html("");
        $('#ds_type_list').html("");
    }
}



function loadGraphClick()
{
    //alert($('#createDatasetButton').attr('batchFile'));
    if ($('#createDatasetButton').attr('batchFile'))
    {
        $('#dataset_creation_message_col').html(addNote(loading_dataset,cl='warning'));
        $.get('/loadGraph',
              data={'batch_file': $('#createDatasetButton').attr('batchFile')},
              function(data)
            {
                  var obj = JSON.parse(data);
                  console.log(obj);
                  $('#dataset_load').val(obj);
                  $('#dataset_creation_message_col').html(addNote(loaded_dataset,cl='success'));

            });
    }
    else
    {
        $('#dataset_creation_message_col').html(addNote(missing_feature));
    }
}


//$('#submit_file_button').addEventListener("click", myScript);
//
//function myScript(){
////    alert("test"),
//    paramname: 'file',
//    maxfiles: 10,
//    maxfilesize: 5,
//    url: '/FileUpload',
//    uploadFinished:function(i,file,response){
//        $.data(file).addClass('done');
//    }
//}


//dropbox.filedrop({
//$("submit_file_button").click(function(){
//    paramname: 'file',
//    maxfiles: 10,
//    maxfilesize: 5,
//    url: '/upload',
//    uploadFinished:function(i,file,response){
//        $.data(file).addClass('done');
//    }
//});

//$("submit_file_button").click(function(){
//    $.post('/FileUpload',
//    {
//        name: "Donald Duck",
//        city: "Duckburg"
//    },
//    function(data, status){
//        alert("Data: " + data + "\nStatus: " + status);
//    });
//});