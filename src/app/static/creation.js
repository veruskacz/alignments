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

   $('#divAdmin').hide();

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

function test(btn)
{
    var status = 'off'
    if (btn.checked) status = 'on'

    $.get('/stardogManagement',
            data = {'status': status},
            function(data)
     {
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
       var ul = document.getElementById('creation_idea_graphtype_list');
       var li = ul.getElementsByTagName('li');
       var num = ('0000' + String(li.length)).substr(-4);
       $('#idea_dataset_counter').html(num);
    });

    $('#creation_idea_registered_graphtype_list').html('Loading...');
    $.get('/getgraphsentitytypes', data = {
                                    'rq_uri': rq_uri,
                                    'mode': 'added',
                                    'function': ''},
                                   function(data)
    {
       $('#creation_idea_registered_graphtype_list').html(data);
       var ul = document.getElementById('creation_idea_registered_graphtype_list');
       var li = ul.getElementsByTagName('li');
       var num = ('0000' + String(li.length)).substr(-4);
       $('#idea_dataset_sel_counter').html(num);
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
      $('#idea_creation_message_col').html(addNote("Please inform the Research Question!"));
   }
}

///////////////////////////////////////////////////////////////////////////////
// Functions for Dataset Inspection & Enrichment
///////////////////////////////////////////////////////////////////////////////
function inspect_dataset_activate(rq_uri)
{
   $('#select_dataset_col').html('Loading...');
//   $.get('/getdatasets',
   $.get('/getdatasetsperrq',
                  data={'rq_uri': rq_uri,
                        'template': 'list_dropdown.html',
                        'function': 'datasetClick(this);dataset_stats_load_linksets_lenses();dataset_stats_load_datasets_predicates();'},
          function(data)
   {  // hide the loading message
      // load the resultant rendered template into source and target buttons
      $('#select_dataset_col').html(data);
   });
}

function getValuesFilterDatasetClick()
{
    var graph_uri = $('#selected_dataset').attr('uri');
//    var entity_type_uri = $('#dts_selected_entity-type').attr('uri');
    var predicate_uri = $('#dataset_selected_pred').attr('uri');
    var search_text = $('#dataset_filter_text').val();

    $.get('/getdatasetpredicatevalues',data={'graph_uri': graph_uri,
                                      'predicate_uri': predicate_uri,
                                      'search_text': search_text,
                                      'function': 'getDatasetPredicateFilteredClick(this, "values-list")',
                                      'template': 'list_group_description.html'},function(data)
    {
       $('#dataset_values_col').html(data);
       var ul = document.getElementById('dataset_values_col');
       var li = ul.getElementsByTagName('li');
       var num = ('0000' + String(li.length)).substr(-4);
       $('#dataset_values_counter').html(num);
       $('#dataset_inspect_selected_pred').html('Select a Property + <span style="color:blue"><strong> example value </strong></span>');
       setAttr('dataset_inspect_selected_pred','uri','');
       $('#dataset_inspect_predicates_col').html('');
    });
}

function getDatasetPredicateFilteredClick(th, ancestorType)
{
    var graph_uri = $('#selected_dataset').attr('uri');
    var entity_type_uri = $('#dts_selected_entity-type').attr('uri');
    var predicate_uri = $('#dataset_selected_pred').attr('uri');
    var sub_uri = $(th).attr('uri');

    list = findAncestor(th, ancestorType);
    var listCol = $(list).attr('targetList');

    selectListItemUnique(th, $(list).attr('id'));

    $.get('/getpredicates', data={'dataset_uri': graph_uri, 'type': '', 'total': '',
                                  'search_uri': sub_uri,
                                  'function': 'selectionClick2(this, "pred-list");'},
                            function(data)
    {  // load the rendered template into the column target list col
        var obj = JSON.parse(data);
        if (obj.message == 'OK')
        {
            $('#'+listCol).html(obj.result);
            var badge_counter = $('#'+listCol).attr('badge_counter');
            var ul = document.getElementById(listCol);
            var li = ul.getElementsByTagName('li');
            var num = ('0000' + String(li.length)).substr(-4);
            $('#'+badge_counter).html(num);
            setAttr(listCol,'graph_uri',graph_uri);
            setAttr(listCol,'sub_uri',sub_uri);
            $('#dataset_inspect_selected_pred').html('Select a Property + <span style="color:blue"><strong> example value </strong></span>');
        }
        else
            $('#'+listCol).html(obj.message);
    });
}

function selectionClick2(th, ancestorType)
{
    list = findAncestor(th, ancestorType);

    var targetTxt = $(list).attr('targetTxt');
    var label = $(th).attr('label');
    var listCol = $(list).attr('targetList');
    var checkPropPath = document.getElementById($(list).attr('propPathCheckBok'));

    // Attributes the uri of the selected entity to the
    // corresponding div where the label is displayed
    // and changes its background color

    // it is not the list of predicates, then just attribute
    // the uri and label to the corresponding divs
    if ((ancestorType != 'pred-list') || !(checkPropPath.checked))
    {   setAttr(targetTxt,'uri', $(th).attr('uri') );
        $('#'+targetTxt).html( label );
//            alert("0");
    }
    // however, if the ancestor is list of predicates, we need to consider the
    // cumulative attribution of values in a property path
    else
    {
        if ( ($('#'+targetTxt).html() == 'Select a Property + <span style="color:blue"><strong> example value </strong></span>') )
        {
//            alert("1");
            setAttr(targetTxt,'uri', $(th).attr('uri') );
            $('#'+targetTxt).html( label );
            var propPath = $(th).attr('uri');
        }
        else if ($('#'+listCol).attr('propPath')!='disabled')
        {
//            alert("2");
            var new_text = $('#'+targetTxt).html() + ' / ' + label;
            var propPath = $('#'+targetTxt).attr('uri') + '/' + $(th).attr('uri');
            setAttr(targetTxt,'uri', propPath );
            $('#'+targetTxt).html( new_text );
        }
        else //replace the last property in the path
        {
            var old_text = $('#'+targetTxt).html();
//            alert(old_text);
            var old_path = $('#'+targetTxt).attr('uri');
//            alert(old_path);
            var index =  old_text.lastIndexOf(" / ");
            var new_text = old_text.substring(0, index) + ' / ' + label;
            index =  old_path.lastIndexOf("/<");
            var propPath = old_path.substring(0, index) + '/' + $(th).attr('uri');
//            alert(propPath);
            setAttr(targetTxt,'uri', propPath );
            $('#'+targetTxt).html( new_text );
            alert(new_text);
        }
    }
    setAttr(targetTxt,'style', 'background-color:lightblue');

    // If a tag optional is provided, change the color of the label accordingly
    var optional = $(th).attr('optional');
    if (optional)
    {
        if (optional == 'true')
        {    label = '<strong><span style="color:red">'+label+'</span></strong>' }
        else
        {    label = '<strong><span style="color:blue">'+label+'</span></strong>' }
    }

    var graph_uri = $(list).attr('graph_uri');
    var sub_uri = $(list).attr('sub_uri');
//    alert(listCol);
//    alert(sub_uri);
    if (listCol)
    {
        //alert($('#'+listCol).attr('propPath'));
        if (ancestorType != 'pred-list')
        {
            setAttr(listCol,'graph_uri',graph_uri);
            // clean previously selected entity type
            targetTxt = $('#'+listCol).attr('targetTxt');

            setAttr(targetTxt,'uri','');
            $('#'+targetTxt).html('Select a Property + <span style="color:blue"><strong> example value </strong></span>');
            setAttr(targetTxt,'style','background-color:none');

            // get the distinct predicates and example values of a graph into a list group
            $('#'+listCol).html('Loading...');

            var total = $(th).attr('total');
            if (!total)
                total = ''
            var type = $(th).attr('uri');
            if (graph_uri == '')
            {
                graph_uri = $(th).attr('uri');
                type = ''
            }

            $.get('/getpredicates', data={'dataset_uri': graph_uri, 'type': type, 'total': total,
                                          'search_uri': sub_uri,
                                          'function': 'selectionClick2(this, "pred-list");'},
                                    function(data)
            {  // load the rendered template into the column target list col
                var obj = JSON.parse(data);
                if (obj.message == 'OK')
                {
                    $('#'+listCol).html(obj.result);
                    if ($('#'+listCol).attr('badge_counter')) {
                       var badge_counter = $('#'+listCol).attr('badge_counter');
                       var ul = document.getElementById(listCol);
                       var li = ul.getElementsByTagName('li');
                       var num = ('0000' + String(li.length)).substr(-4);
                       $('#'+badge_counter).html(num);
                    }

                }
                else
                    $('#'+listCol).html(obj.message);
            });
        }
        else if ((checkPropPath.checked) && ($('#'+listCol).attr('propPath')!='disabled'))
        {
            // check if the value of the selected property is of type uri
            if ($(th).attr('obj_type') == 'uri')
            {    // if the user choose to use property path
                // then the pred-list will be reloaeded with the predicates
                // that are available for the objects of the selected property
                // if (property_path is selected)
                var previousContentListCol = $('#'+listCol).html();
                $('#'+listCol).html('Loading...');
                $.get('/getpredicates', data={'dataset_uri': graph_uri, 'propPath': propPath,
                                          'search_uri': sub_uri,
                                          'function': 'selectionClick2(this, "pred-list");'},
                                    function(data)
                {  // load the rendered template into the column target list col
                    var obj = JSON.parse(data);
                    if (obj.message == 'OK')
                    {    $('#'+listCol).html(obj.result);
                        if ($('#'+listCol).attr('badge_counter')) {
                           var badge_counter = $('#'+listCol).attr('badge_counter');
                           var ul = document.getElementById(listCol);
                           var li = ul.getElementsByTagName('li');
                           var num = ('0000' + String(li.length)).substr(-4);
                           $('#'+badge_counter).html(num);
                        }
                    }
                    else
                    { if (obj.message == 'Empty')
                        {    // it is a uri but not a valid property path
                            // restore the preivous content
                            $('#'+listCol).html(previousContentListCol);
                            // disable the continuation of property path
                            setAttr(listCol,'propPath','disabled');
                        }
                        else
                        {    $('#'+listCol).html(obj.message); }
                    }
                });
            }
            else
            {
                setAttr(listCol,'propPath','disabled');
            }
        }
    }
}

function geoEnrichmentClick()
{

    var graph = $('#selected_dataset').attr('uri');
    var entity_datatype = $('#dts_selected_entity-type').attr('uri');
    var long_predicate = $('#long_selected_pred').attr('uri');
    var lat_predicate = $('#lat_selected_pred').attr('uri');

    if ((graph) && (entity_datatype) && (long_predicate) && (lat_predicate))
    {
       var message = "Executing the dataset geo-enrichement";
       $('#geoenrichment_message_col').html(addNote(message,cl='warning'));
       loadingGif(document.getElementById('geoenrichment_message_col'), 2);
       $.get('/enrichdataset',
                      data={'graph': graph,
                            'entity_datatype': entity_datatype,
                            'long_predicate': long_predicate,
                            'lat_predicate': lat_predicate
                            },
              function(data)
       {
          loadingGif(document.getElementById('geoenrichment_message_col'), 2, show=false);
          var obj = JSON.parse(data);
          $('#geoenrichment_message_col').html(addNote(obj.message,cl='info'));
       });

    }
    else {
      $('#geoenrichment_message_col').html(addNote(missing_feature));
    }

}



///////////////////////////////////////////////////////////////////////////////
// Functions called at onclick of the buttons in linksetsCreation.html
///////////////////////////////////////////////////////////////////////////////

// Button that activates the inspect div for either inspect, refine or import modes
function inspect_linkset_activate(mode)
{

  var rq_uri = $('#creation_linkset_selected_RQ').attr('uri');
//    setAttr("inspect_linkset_selection_col","unique","enabled");

  if (rq_uri)
  {
     $('#creation_linkset_row').hide();
     refresh_create_linkset();

     $('#inspect_linkset_selection_col').html('Loading...');
     $.get('/getgraphsperrqtype',
                  data={'rq_uri': rq_uri,
                        'mode': mode,
                        'type': 'linkset',
                        'template': 'list_group.html'},
                  function(data)
     {
       $('#inspect_linkset_selection_col').html(data);
       var ul = document.getElementById('inspect_linkset_selection_col');
       var a = ul.getElementsByTagName('a');
       var num = ('0000' + String(a.length)).substr(-4);
       $('#linkset_counter').html(num);

       // set actions after clicking a graph in the list
       $('#inspect_linkset_selection_col a').on('click',function(e)
        {
          if ((mode == 'export') && ($('#exportLinksetButton').attr('mode')=='vis'))
          {
            var selection = selectListItem(this);
//            alert(selection);
          }
          else
          {
            var selection = selectListItemUnique(this, 'inspect_linkset_selection_col')
          }
          if (selection)
          {
            var linkset_uri = $(this).attr('uri');

            // load the panel describing the linkset sample
            $('#inspect_linkset_linkset_details_col').show();
            $('#inspect_linkset_linkset_details_col').html('Loading...');
            $.get('/getlinksetdetails',data={'linkset': linkset_uri},function(data)
            {
                var obj = JSON.parse(data);
                $('#inspect_linkset_linkset_details_col').html(obj.data);

                get_filter(rq_uri, linkset_uri);

                if (mode == 'refine' || mode == 'edit' || mode == 'reject-refine' || mode == 'export')
                {
                   $('#creation_linkset_row').show();
                   loadEditPanel(obj.metadata, mode);
                   enableButton('deleteLinksetButton');
                   enableButton('exportLinksetButton');
                   enableButton('exportPlotLinksetButton');
                }
                else if (mode == 'inspect')
                {
                   $('#creation_linkset_filter_row').show();
                   $('#creation_linkset_search_row').show();
                   $('#creation_linkset_correspondence_row').show();
                   showDetails(rq_uri, linkset_uri, obj.metadata, filter_uri='none');
                }
            });

          }
          else { $('#inspect_linkset_linkset_details_col').html(""); }
          e.preventDefault();
          return false;
        });
     });
  }


  if (mode == 'import') {
    $('#import_heading_panel').show();
    $('#inspect_heading_panel').hide();
  }
  else {
    if (mode == 'refine') {
      $('#item_identity').hide();
    }
    if (mode == 'edit') {
      $('#inspect_panel_body').hide();
      $('#creation_linkset_row').show();
      $('#edit_linkset_heading').show();
      enableButton('deleteLinksetButton', enable=false);
    }
    else if (mode == 'export') {
      $('#inspect_panel_body').hide();
      $('#creation_linkset_row').show();
      $('#export_linkset_heading').show();
      enableButton('exportLinksetButton', enable=false);
      enableButton('exportPlotLinksetButton', enable=false);
    }
    else
    {
      $('#inspect_panel_body').show();
    }
    $('#inspect_heading_panel').show();
    $('#import_heading_panel').hide();
  }
}


function loadEditPanel(obj, mode)
{
    setAttr('hidden_src_div','uri',obj.subTarget.value);
    setAttr('hidden_src_div','label',obj.subTarget_stripped.value);

    setAttr('hidden_trg_div','uri',obj.objTarget.value);
    setAttr('hidden_trg_div','label',obj.objTarget_stripped.value);

    setAttr('hidden_src_entType_div','uri',obj.s_datatype.value);
    setAttr('hidden_src_entType_div','label',obj.s_datatype_stripped.value);

    setAttr('hidden_trg_entType_div','uri',obj.o_datatype.value);
    setAttr('hidden_trg_entType_div','label',obj.o_datatype_stripped.value);

    // just do nothing while it is not implemented
    if (mode == 'edit')
        mode = ''

    if (mode == 'refine' || mode == 'edit')
    {
        datasetClick(document.getElementById('hidden_src_div'));
        datasetClick(document.getElementById('hidden_trg_div'));

        setAttr('hidden_src_div','uri','');
        setAttr('hidden_src_div','label','');

        setAttr('hidden_trg_div','uri','');
        setAttr('hidden_trg_div','label','');
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


    if (mode == 'refine' || mode == 'edit')
    {
        var ancestorType = "entity-list";

        selectionClick(document.getElementById('hidden_src_entType_div'), ancestorType);
        selectionClick(document.getElementById('hidden_trg_entType_div'), ancestorType);

        setAttr('hidden_src_entType_div','uri','');
        setAttr('hidden_src_entType_div','label','');

        setAttr('hidden_trg_entType_div','uri','');
        setAttr('hidden_trg_entType_div','label','');

    }
    else
    {
        setAttr('src_selected_entity-type','uri',obj.s_datatype.value);
        setAttr('src_selected_entity-type','style','background-color:lightblue');
        $('#src_selected_entity-type').html(obj.s_datatype_stripped.value);

        setAttr('trg_selected_entity-type','uri',obj.o_datatype.value);
        setAttr('trg_selected_entity-type','style','background-color:lightblue');
        $('#trg_selected_entity-type').html(obj.o_datatype_stripped.value);
    }

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
   {
      $('#src_datasets_row').show();
      $('#src_entitytype_row').show();
      $('#trg_datasets_row').show();
      $('#trg_entitytype_row').show();
      // load the resultant rendered template into source and target buttons
      $('#button-src-col').html(data);
      $('#button-trg-col').html(data);
   });
   //TODO: Find a more efficient way to re-settle the function for the items onclick
   $('#button-src-enriched-col').html('Loading...');
   $('#button-trg-enriched-col').html('Loading...');
   $.get('/getdatasetsperrq',
          data = {'template': 'list_dropdown.html',
                  'rq_uri': $('#creation_linkset_selected_RQ').attr('uri'),
                  'function': 'selectionClick(this, "graph-list");'},
          function(data)
   {
      $('#button-src-enriched-col').html(data);
      $('#button-trg-enriched-col').html(data);
   });
}


// Button that actually creates the linkset
// it checks the selected elements and assemble them into dictionaries
// be passed as parameters to the request /createLinkset
function createLinksetClick()
{
    $('#linkset_creation_message_col').html("");

    var reducer = ''; intermediate = '';
    if ($('#selected_meth').attr('uri') != 'intermediate')
     {   reducer = $('#selected_int_red_graph').attr('uri'); }
    else
     {   intermediate = $('#selected_int_red_graph').attr('uri'); }

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
                  'entity_datatype': $('#src_selected_entity-type').attr('uri'),
                  'additional_entity_type_pred': additional_entity_type_pred,
                  'additional_entity_type_value': additional_entity_type_value,
                  'reducer': reducer};
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
                  'entity_datatype': $('#trg_selected_entity-type').attr('uri'),
                  'additional_entity_type_pred': additional_entity_type_pred,
                  'additional_entity_type_value': additional_entity_type_value,
                  'reducer': reducer};
    }

    if ((Object.keys(srcDict).length) &&
        (Object.keys(trgDict).length) &&
        ($('#selected_meth').attr('uri')) &&
        ($('#selected_meth').attr('uri') != 'intermediate' || intermediate) &&
        ($('#selected_meth').attr('uri') != 'approxNbrSim' ||
            ($('#linkset_approx_delta').val() && $('#linkset_approx_num_type').find("option:selected").text() )
            )
        )
    {
        var specs = {
          'rq_uri': $('#creation_linkset_selected_RQ').attr('uri'),
          'src_graph': $('#src_selected_graph').attr('uri'),
          'src_aligns': $('#src_selected_pred').attr('uri'),
          'src_entity_datatype': $('#src_selected_entity-type').attr('uri'),
          //'src_reducer': reducer,

          'trg_graph': $('#trg_selected_graph').attr('uri'),
          'trg_aligns': $('#trg_selected_pred').attr('uri'),
          'trg_entity_datatype': $('#trg_selected_entity-type').attr('uri'),
          //'trg_reducer': reducer,

          'mechanism': $('#selected_meth').attr('uri'),

          'intermediate_graph': intermediate,

          'stop_words': $('#linkset_approx_stop_words').val(),
          'stop_symbols': $('#linkset_approx_symbols').val(),
          'threshold': $('#linkset_approx_threshold').val(),

          'delta': $('#linkset_approx_delta').val() ,
          'numeric_approx_type': $('#linkset_approx_num_type').find("option:selected").text(),

          //'corrsp_reducer': reducer
        }

        multiple_entries = 'no'
        if (multiple_entries == 'yes')
            specs['corrsp_reducer'] = reducer
        else {
            specs['src_reducer'] = reducer
            specs['trg_reducer'] = reducer }

        var message = "EXECUTING YOUR LINKSET SPECS.</br>PLEASE WAIT UNTIL THE COMPLETION OF YOUR EXECUTION";
        $('#linkset_creation_message_col').html(addNote(message,cl='warning'));
        loadingGif(document.getElementById('linkset_creation_message_col'), 2);

        // call function that creates the linkset
        // HERE!!!!
        $.ajax(

        {
            url: '/createLinkset',
            data: specs,
            type: "GET",
            timeout: 0,
            success: function(data){
                loadingGif(document.getElementById('linkset_creation_message_col'), 2, show=false);
                var obj = JSON.parse(data);
                $('#linkset_creation_message_col').html(addNote(obj.message,cl='info'));
            }
        }

//        '/createLinkset', specs, function(data, status)
//        }
//        {
//              console.log(status)
//              loadingGif(document.getElementById('linkset_creation_message_col'), 2, show=false);
//              var obj = JSON.parse(data);
//              $('#linkset_creation_message_col').html(addNote(obj.message,cl='info'));
//        }

        );
    }
    else {
      $('#linkset_creation_message_col').html(addNote(missing_feature));
    }
}


function refineLinksetClick()
{

  var reducer = ''; intermediate = '';
  if ($('#selected_meth').attr('uri') != 'intermediate')
   {   reducer = $('#selected_int_red_graph').attr('uri'); }
  else
   {   intermediate = $('#selected_int_red_graph').attr('uri'); }

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
  var elems = selectedElemsInGroupList('inspect_linkset_selection_col');
  if (elems.length > 0) // it should have only one selected
  {
    linkset = $(elems[0]).attr('uri');
  }

 if ((Object.keys(srcDict).length) &&
        (Object.keys(trgDict).length) &&
        ($('#selected_meth').attr('uri')) &&
        ($('#selected_meth').attr('uri') != 'intermediate' || intermediate) &&
      (linkset) &&
        ($('#selected_meth').attr('uri') != 'approxNbrSim' ||
            ($('#linkset_approx_delta').val() && $('#linkset_approx_num_type').val() ))
      )
  {

      var specs = {
        'rq_uri': $('#creation_linkset_selected_RQ').attr('uri'),
        'linkset_uri': linkset,

        'src_graph': $('#src_selected_graph').attr('uri'),
        'src_aligns': $('#src_selected_pred').attr('uri'),
        'src_entity_datatye': $('#src_selected_entity-type').attr('uri'),
        'src_reducer': reducer,
        'src_graph_enriched': $('#src_selected_graph_enriched').attr('uri'),

        'trg_graph': $('#trg_selected_graph').attr('uri'),
        'trg_aligns': $('#trg_selected_pred').attr('uri'),
        'trg_entity_datatye': $('#trg_selected_entity-type').attr('uri'),
        'trg_reducer': reducer,
        'trg_graph_enriched': $('#trg_selected_graph_enriched').attr('uri'),

        'mechanism': $('#selected_meth').attr('uri'),

        'intermediate_graph': intermediate,

        'delta': $('#linkset_approx_delta').val() ,
        'numeric_approx_type': $('#linkset_approx_num_type').val()
      }

      var message = "EXECUTING YOUR LINKSET SPECS.</br>PLEASE WAIT UNTIL THE COMPLETION OF YOUR EXECUTION";
      $('#linkset_refine_message_col').html(addNote(message,cl='warning'));
      loadingGif(document.getElementById('linkset_refine_message_col'), 2);

      // call function that creates the linkset
      // HERE!!!!
      $.get('/refineLinkset', specs, function(data)
      {
            var obj = JSON.parse(data);
            $('#linkset_refine_message_col').html(addNote(obj.message,cl='info'));
            loadingGif(document.getElementById('linkset_refine_message_col'), 2, show=false);
      });

  }
  else {
    $('#linkset_refine_message_col').html(addNote(missing_feature));
  }
}


function exportPlotLinksetClick(elem)
{
//    var credentials = { 'user': $("#modalPlotPass #usrname").val().trim(),
//                        'password': $("#modalPlotPass #pssw").val().trim()}
    exportLinksetClick("export.ttl",mode="vis", user= $("#modalPlotPass #usrname").val().trim(), psswd=$("#modalPlotPass #pssw").val().trim() );
//    $(elem).dialog("close");
}

// TODO: make a single call for lens and linkset
function exportPlotLensClick(elem)
{
//    var credentials = { 'user': $("#modalPlotPass #usrname").val().trim(),
//                        'password': $("#modalPlotPass #pssw").val().trim()}
    exportLensClick("export.ttl",mode="vis", user= $("#modalLensPlotPass #LensUsrname").val().trim(), psswd=$("#modalLensPlotPass #LensPssw").val().trim() );
//    $(elem).dialog("close");
}

function exportLinksetClick(filename, mode='flat', user='', psswd='')
{
    var linkset = '';
    var elems = selectedElemsInGroupList('inspect_linkset_selection_col');
    if (elems.length > 0) // if any element is selected
    {
        linkset = $(elems[0]).attr('uri');  // it should have only one selected

        // if plot is requested, a list of graphs is the input
        var graphs = []
        if (mode == 'vis')
        {
            var i;
            for (i = 0; i < elems.length; i++) {
              graphs.push($(elems[i]).attr('uri'));
            }
        }

        var message = "Exporting Linkset";
        $('#linkset_export_message_col').html(addNote(message,cl='warning'));
        loadingGif(document.getElementById('linkset_export_message_col'), 2);

        $.ajax({
            url: "/exportAlignment",
            data: {'graph_uri':linkset,
                                                'graphs[]':graphs,
                                                'name': user,
                                                'code': psswd,
                                                'mode':mode},
            dataType: "text",
            success: function(data){

            var obj = JSON.parse(data);
            loadingGif(document.getElementById('linkset_export_message_col'), 2, show=false);

            $('#linkset_export_message_col').html(addNote(obj.message,cl='info'));
            csv = obj.result;

             var blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
                        var link = document.createElement("a");
                        if (link.download !== undefined) { // feature detection
                            // Browsers that support HTML5 download attribute
                            var url = URL.createObjectURL(blob);
                            link.setAttribute("href", url);
                            link.setAttribute("download", filename);
                            link.style.visibility = 'hidden';
                            document.body.appendChild(link);
                            link.click();
                            document.body.removeChild(link);
                        }

            }
        });
    }
}


function exportLensClick(filename, mode='flat', user='', psswd='')
{
    var lens = '';
    var elems = selectedElemsInGroupList('inspect_lens_lens_selection_col');
    if (elems.length > 0) // if any element is selected
    {
        lens = $(elems[0]).attr('uri');  // it should have only one selected

        // if plot is requested, a list of graphs is the input
        var graphs = []
        if (mode == 'vis')
        {
            var i;
            for (i = 0; i < elems.length; i++) {
              graphs.push($(elems[i]).attr('uri'));
            }
        }

        var message = "Exporting Lens";
        $('#lens_export_message_col').html(addNote(message,cl='warning'));
        loadingGif(document.getElementById('lens_export_message_col'), 2);

        // call function that creates the linkset
//        $.get('/exportAlignment', data={'graph_uri':lens}, function(data)
//        {
//
//            var obj = JSON.parse(data);
//            loadingGif(document.getElementById('lens_export_message_col'), 2, show=false);
//
//            $('#lens_export_message_col').html(addNote(obj.message,cl='info'));
//            csv = obj.result;
//
//            var element = document.createElement('a');
//            element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(csv));
//            element.setAttribute('download', filename);
//
//            element.style.display = 'none';
//            document.body.appendChild(element);
//
//            element.click();
//
//            document.body.removeChild(element);
//        });

        $.ajax({
            url: "/exportAlignment",
            data: {'graph_uri':lens,
                                                'graphs[]':graphs,
                                                'name': user,
                                                'code': psswd,
                                                'mode': mode},
            dataType: "text",
            success: function(data){

            var obj = JSON.parse(data);
            loadingGif(document.getElementById('lens_export_message_col'), 2, show=false);

            $('#lens_export_message_col').html(addNote(obj.message,cl='info'));
            csv = obj.result;

             var blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
                        var link = document.createElement("a");
                        if (link.download !== undefined) { // feature detection
                            // Browsers that support HTML5 download attribute
                            var url = URL.createObjectURL(blob);
                            link.setAttribute("href", url);
                            link.setAttribute("download", filename);
                            link.style.visibility = 'hidden';
                            document.body.appendChild(link);
                            link.click();
                            document.body.removeChild(link);
                        }

            }
        });

    }
}

function importLinksetClick()
{
    var rq_uri = $('#creation_linkset_selected_RQ').attr('uri');

    var elems = selectedElemsInGroupList('inspect_linkset_selection_col');
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
        loadingGif(document.getElementById('linkset_import_message_col'), 2);

        // call function that creates the linkset
        $.get('/importLinkset', data, function(data)
        {
            $('#linkset_import_message_col').html(addNote(data,cl='info'));
            loadingGif(document.getElementById('linkset_import_message_col'), 2, show=false);
        });
    }
    else {
      $('#linkset_import_message_col').html(addNote(missing_feature));
    }
}

//
//function editLabelViewClick(elem)
//{
//    var rq_uri = $('#creation_view_selected_RQ').attr('uri');
//    var view = '';
//    var elems = selectedElemsInGroupList('inspect_views_selection_col');
//    if (elems.length > 0) // if any element is selected
//    {
//        view = $(elems[0]).attr('uri');  // it should have only one selected
//
//        var label = $("#myModal #viewLabel").val().trim();
//        if (label)
//        {
//            //        alert(test);
//            $.get('/updateViewLabel', data={'rq_uri':rq_uri, 'view_uri':view, 'view_label':label}, function(data)
//            {
//                var obj = JSON.parse(data);
//                if (obj.result == 'OK')
//                {   $('#btn_edit_view').click();
//                    $('#view_edit_message_col').html(addNote(obj.message,cl='info')); }
//                else
//                {    $('#view_edit_message_col').html(addNote(obj.message)); }
//            });
//        }
//    }
//    $(elem).dialog("close");
//}

$("#labelLinksetModal").on("shown.bs.modal", function(e) {
//$( "#labelLinksetModal" ).on('shown', function(){
//    alert("I want this to appear after the modal has opened!");
    var label = '';
    var elems = selectedElemsInGroupList('inspect_linkset_selection_col');
    if (elems.length > 0) // if any element is selected
    {
        label = $(elems[0]).attr('label');  // it should have only one selected
    }
    $('#linksetLabel').val(label);
});

$("#labelLensModal").on("shown.bs.modal", function(e) {
//$( "#labelLinksetModal" ).on('shown', function(){
//    alert("I want this to appear after the modal has opened!");
    var label = '';
    var elems = selectedElemsInGroupList('inspect_lens_lens_selection_col');
    if (elems.length > 0) // if any element is selected
    {
        label = $(elems[0]).attr('label');  // it should have only one selected
    }
    $('#lensLabel').val(label);
});

$("#labelViewModal").on("shown.bs.modal", function(e) {
//$( "#labelLinksetModal" ).on('shown', function(){
//    alert("I want this to appear after the modal has opened!");
    var label = '';
    var elems = selectedElemsInGroupList('inspect_views_selection_col');
    if (elems.length > 0) // if any element is selected
    {
        label = $(elems[0]).attr('label');  // it should have only one selected
    }
    $('#viewLabel').val(label);
});

function editLabelClick(label, type='linkset') {
    if (type == 'linkset') {
        var rq_uri = $('#creation_linkset_selected_RQ').attr('uri');
        var elems = selectedElemsInGroupList('inspect_linkset_selection_col');
        var msg_col = 'linkset_edit_message_col';
        var refresh_btn = 'btn_edit_linkset'}
    else if (type == 'lens') {
        var rq_uri = $('#creation_lens_selected_RQ').attr('uri');
        var elems = selectedElemsInGroupList('inspect_lens_lens_selection_col');
        var msg_col = 'lens_edit_message_col';
        var refresh_btn = 'btn_edit_lens'}
    else { // if (type == 'view') {
        var rq_uri = $('#creation_view_selected_RQ').attr('uri');
        var elems = selectedElemsInGroupList('inspect_views_selection_col');
        var msg_col = 'view_edit_message_col';
        var refresh_btn = 'btn_edit_view'
    }
    if (elems.length > 0) // if any element is selected
    {
        uri = $(elems[0]).attr('uri');  // it should have only one selected

        //var label = $("#labelLinksetModal #linksetLabel").val().trim();
        if (label)
        {
            $.get('/updateLabel', data={'rq_uri':rq_uri, 'graph_uri':uri, 'label':label}, function(data)
            {
                var obj = JSON.parse(data);
                if (obj.result == 'OK')
                {
                    $('#'+refresh_btn).click();
                    //elem[0].setAttribute("label", label);
                    $('#'+msg_col).html(addNote(obj.message,cl='info')); }
                else
                {   $('#'+msg_col).html(addNote(obj.message)); }
            });
        }
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


function deleteLinksetClick()
{
    var rq_uri = $('#creation_linkset_selected_RQ').attr('uri');
    var linkset = '';
    var elems = selectedElemsInGroupList('inspect_linkset_selection_col');
    if (elems.length > 0) // if any element is selected
    {
        linkset = $(elems[0]).attr('uri');  // it should have only one selected
        //alert(linkset);
        var message = "Checking for linkset dependencies...";
        $('#linkset_edit_message_col').html(addNote(message,cl='warning'));
        loadingGif(document.getElementById('linkset_edit_message_col'), 2);

        // call function that creates the linkset
        $.get('/deleteLinkset', data={'rq_uri':rq_uri, 'linkset_uri':linkset, 'mode':'check'}, function(data)
        {
            var obj = JSON.parse(data);
            if (obj.message == 'OK')
            {   var test = confirm("Delete the linkset?");
                if (test)
                {
                    var message = "Deleting Linkset...";
                    $('#linkset_edit_message_col').html(addNote(message,cl='warning'));

                    $.get('/deleteLinkset', data={'rq_uri':rq_uri, 'linkset_uri':linkset, 'mode':'delete'}, function(data)
                    {
                        var obj = JSON.parse(data);
                        if (obj.result == 'OK')
                        {   $('#btn_edit_linkset').click();
                            $('#linkset_edit_message_col').html(addNote(obj.message,cl='info')); }
                        else
                        {    $('#linkset_edit_message_col').html(addNote(obj.message)); }

                        loadingGif(document.getElementById('linkset_edit_message_col'), 2, show=false);
                    });
                }
                else
                {   $('#linkset_edit_message_col').html('');
                    loadingGif(document.getElementById('linkset_edit_message_col'), 2, show=false);
                }
            }
            else if (obj.message == 'Check Dependencies')
            {
                $('#linkset_edit_message_col').html(addNote(obj.result));
                loadingGif(document.getElementById('linkset_edit_message_col'), 2, show=false);
            }
            else
            {
                $('#linkset_edit_message_col').html(addNote(obj.message));
                loadingGif(document.getElementById('linkset_edit_message_col'), 2, show=false);
            }
        });
    }
}


function addFilterLinksetClick()
{
    var rq_uri = $('#creation_linkset_selected_RQ').attr('uri');
    var linkset = '';
    var property = '';
    var value_1 = {};
    var value_2 = {};
    var elems = selectedElemsInGroupList('inspect_linkset_selection_col');
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
        $.get('/setfilter',
                  data={'rq_uri': rq_uri,
                        'graph_uri': linkset,
                        'property': property,
                        'value_1': JSON.stringify(value_1),
                        'value_2': JSON.stringify(value_2)},
                  function(data)
        {
            var obj = JSON.parse(data);
            get_filter(rq_uri, linkset, obj.result, type='linkset');
        });
    }
}

function addFilterLensClick()
{
    var rq_uri = $('#creation_lens_selected_RQ').attr('uri');
    var lens = '';
    var property = '';
    var value_1 = {};
    var value_2 = {};
    var elems = selectedElemsInGroupList('inspect_lens_lens_selection_col');
    if (elems.length > 0) // it should have only one selected
    {
        lens = $(elems[0]).attr('uri');
        property = $('#lens_filter_property').find("option:selected").text();
        var operator = '';
        if ($('#lens_filter_value1').val())
        {
            if ($('#lens_value1_greater').is(':checked'))
            {
                operator += $('#lens_value1_greater').val();
            }
            if ($('#lens_value1_equal').is(':checked'))
            {
                operator += $('#lens_value1_equal').val();
            }
            if (operator)
            {
                value_1 = {'value': $('#lens_filter_value1').val(),
                           'operator': operator }
            }
        }
        operator = '';
        if ($('#lens_filter_value2').val())
        {
            if ($('#lens_value2_smaller').is(':checked'))
            {
                operator += $('#lens_value2_smaller').val();
            }
            if ($('#lens_value2_equal').is(':checked'))
            {
                operator += $('#lens_value2_equal').val();
            }
            if (operator)
            {
                value_2 = {'value': $('#lens_filter_value2').val(),
                           'operator': operator }
            }
        }
    }
    if ((rq_uri != '') && (lens != '') && (property!='--Select a Property--') &&
        ((value_1 != {}) || (value_2 != {})) )
    {
        $.get('/setfilter',
                  data={'rq_uri': rq_uri,
                        'graph_uri': lens,
                        'property': property,
                        'value_1': JSON.stringify(value_1),
                        'value_2': JSON.stringify(value_2)},
                  function(data)
        {
            var obj = JSON.parse(data);
            get_filter(rq_uri, lens, obj.result, type='lens');
        });
    }
}

function applyFilterLinksetClick()
{
    var rq_uri = $('#creation_linkset_selected_RQ').attr('uri');
    var linkset_uri = ''
    var elems = selectedElemsInDiv("inspect_linkset_selection_col");
       if (elems.length > 0)
       {    linkset_uri = $(elems[0]).attr('uri');
       }

    var filter_uri = '';
    elems = selectedElemsInDiv("linkset_filter_col");
    if (elems.length > 0)
        { filter_uri = $(elems[0]).attr('uri'); }
    var filter_term =  $('#linkset_filter_text').val();
    if (filter_term == "-- Type a term for search & filter --")
        { filter_term = ''; }

    $.get('/getlinksetdetails',data={'linkset': linkset_uri,
                                      'template': 'none',
                                      'rq_uri': rq_uri,
                                      'filter_uri': filter_uri},function(data)
    {
       var obj = JSON.parse(data);

       $('#creation_linkset_filter_row').show();
       $('#creation_linkset_search_row').show();
       $('#creation_linkset_correspondence_row').show();
       showDetails(rq_uri, linkset_uri, obj, filter_uri, filter_term);
    });
}


function deleteFilterLinksetClick()
{
    var rq_uri = $('#creation_linkset_selected_RQ').attr('uri');
    var linkset_uri = ''
    var elems = selectedElemsInDiv("inspect_linkset_selection_col");
    if (elems.length > 0)
    {    linkset_uri = $(elems[0]).attr('uri');
    }

    var filter_uri = '';
    elems = selectedElemsInDiv("linkset_filter_col");
    if (elems.length > 0)
    {   filter_uri = $(elems[0]).attr('uri');

        var test = confirm("Delete the filter?");
        if (test)
        {
            var message = "Deleting Filter";
            $('#linkset_add_filter_message_col').html(addNote(message,cl='warning'));

            $.get('/deleteFilter',data={'rq_uri': rq_uri,
                                        'filter_uri': filter_uri},function(data)
            {
               var obj = JSON.parse(data);
               $('#linkset_add_filter_message_col').html(addNote(obj.message,cl='warning'));
               get_filter(rq_uri, linkset_uri, '', type='linkset');
            });
        }
    }
}

function deleteFilterLensClick()
{
    var rq_uri = $('#creation_lens_selected_RQ').attr('uri');
    var lens_uri = ''
    var elems = selectedElemsInDiv("inspect_lens_lens_selection_col");
    if (elems.length > 0)
    {    lens_uri = $(elems[0]).attr('uri');
    }

    var filter_uri = '';
    elems = selectedElemsInDiv("lens_filter_col");
    if (elems.length > 0)
    {   filter_uri = $(elems[0]).attr('uri');

        var test = confirm("Delete the filter?");
        if (test)
        {
            var message = "Deleting Filter";
            $('#lens_add_filter_message_col').html(addNote(message,cl='warning'));

            $.get('/deleteFilter',data={'rq_uri': rq_uri,
                                        'filter_uri': filter_uri},function(data)
            {
               var obj = JSON.parse(data);
               $('#lens_add_filter_message_col').html(addNote(obj.message,cl='warning'));
               get_filter(rq_uri, lens_uri, '', type='lens');
            });
        }
    }
}

function applyFilterLensClick()
{
    var rq_uri = $('#creation_lens_selected_RQ').attr('uri');
    var lens_uri = ''
    var elems = selectedElemsInDiv("inspect_lens_lens_selection_col");
       if (elems.length > 0)
       {    lens_uri = $(elems[0]).attr('uri');
       }

    var filter_uri = '';
    elems = selectedElemsInDiv("lens_filter_col");
    if (elems.length > 0)
        { filter_uri = $(elems[0]).attr('uri'); }
    var filter_term =  $('#lens_filter_text').val();
    if (filter_term == "-- Type a term --")
        { filter_term = ''; }

    $.get('/getlensdetails',data={'lens': lens_uri,
                                                'template': 'none'},function(data)
    {
       var obj = JSON.parse(data);

       $('#creation_lens_filter_row').show();
       $('#creation_lens_search_row').show();
       $('#creation_lens_correspondence_row').show();
       showDetails(rq_uri, lens_uri, obj, filter_uri, filter_term);
    });
}

function get_filter(rq_uri, graph_uri, filter_uri='', type='linkset')
{
    if (type == 'linkset')
        var list_col = 'linkset_filter_list';
    else
        var list_col = 'lens_filter_list';

//    alert(list_col);
    $.get('/getfilters',data={'rq_uri': rq_uri, 'graph_uri': graph_uri},function(data)
    {
        $('#'+list_col).html(data);
//        alert(data);

        var item = '<li class="list-group-item list-group-item-warning" uri="none" ' //id="no_filter_linkset" '
                            + '"><span class="list-group-item-heading"> None </span></li>';
        $('#'+list_col).prepend(item);

//        if (filter_uri != '')
//            selectListItemUnique(this, list_col)

        $('#' + list_col + ' li').on('click',function()
        {   selectListItemUnique(this, list_col)
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
  $('#lens_inspect_panel_body').hide();
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
       var ul = document.getElementById('inspect_lens_lens_selection_col');
       var a = ul.getElementsByTagName('a');
       var num = ('0000' + String(a.length)).substr(-4);
       $('#lens_counter').html(num);

      // set actions after clicking a graph in the list
      $('#inspect_lens_lens_selection_col a').on('click',function()
       {
          if (selectListItemUnique(this, 'inspect_lens_lens_selection_col'))
          {
            var lens_uri = $(this).attr('uri');

            // load the panel describing the lens
             $('#inspect_lens_lens_details_col').html('Loading...');

             $.get('/getlensspecs',data={'lens': lens_uri},function(data)
             { $('#inspect_lens_lens_details_col').html(data);
             });

            if (mode == 'edit')
            {
                $('#creation_lens_row').show();
                enableButton('deleteLensButton');
            }
            else if (mode == 'export')
            {
                $('#creation_lens_row').show();
                enableButton('exportLensButton');
            }
            else if (mode == 'refine')
            {
                $('#refine_lens_heading').show();
                $('#lens_inspect_panel_body').show();
                $('#lens_refine_row').show();
                $('#refine_lens_row').show();
//                enableButton('RefineLensButton');
//                var obj = { subTarget: 'http://goldenagents.org/datasets/003MarriageRegistries',
//                            objTarget: 'http://goldenagents.org/datasets/002BaptismRegistries',
//                            s_datatype: 'http://goldenagents.org/uva/SAA/ontology/Person',
//                            o_datatype: 'http://goldenagents.org/uva/SAA/ontology/Person' };
                  $.get('/getlensrefinedetails',data={'lens': lens_uri},function(data)
                  {
                    var obj = JSON.parse(data);
                    loadLensRefinePanel(obj);
                  });
            }
            else
            {
                // load the panel for filter
                  $('#creation_lens_filter_row').show();
                  $('#creation_lens_search_row').show();

                // load the panel for correspondences details
                  $('#creation_lens_correspondence_row').show();
                  //already has Loading...
                  $.get('/getlensdetails',data={'lens': lens_uri,
                                                'template': 'none'},function(data)
                  {
                    var obj = JSON.parse(data);
                    showDetails(rq_uri, lens_uri, obj);

                  });

//                 alert(rq_uri);
                 get_filter(rq_uri, lens_uri, filter_uri='', type='lens');

            }
          }
        });
    });

    if (mode == 'edit') {
      $('#lens_inspect_panel_body').hide();
      $('#creation_lens_filter_row').hide();
      $('#creation_lens_search_row').hide();
      $('#creation_lens_correspondence_row').hide();
      $('#creation_lens_row').show();
      $('#edit_lens_heading').show();
      enableButton('deleteLensButton', enable=false);
    }
    else if (mode == 'export') {
      $('#lens_inspect_panel_body').hide();
      $('#creation_lens_filter_row').hide();
      $('#creation_lens_search_row').hide();
      $('#creation_lens_correspondence_row').hide();
      $('#creation_lens_row').show();
      $('#export_lens_heading').show();
      enableButton('exportLensButton', enable=false);
    }
    else if (mode == 'refine') {
      $('#lens_creation_row').hide();
      $('#creation_lens_filter_row').hide();
      $('#creation_lens_search_row').hide();
      $('#creation_lens_correspondence_row').hide();
      $('#creation_lens_row').show();
//      enableButton('exportLensButton', enable=false);
    }
    else
    { $('#lens_inspect_panel_body').show(); }

  }
}


function loadLensRefinePanel(obj)
{
    setAttr('refine_lens_hidden_src_div','uri',obj.subTarget);
    setAttr('refine_lens_hidden_src_div','label',obj.subTarget_label);

    setAttr('refine_lens_hidden_trg_div','uri',obj.objTarget);
    setAttr('refine_lens_hidden_trg_div','label',obj.objTarget_label);

    setAttr('refine_lens_hidden_src_entType_div','uri',obj.s_datatype);
    setAttr('refine_lens_hidden_src_entType_div','label',obj.s_datatype_label);

    setAttr('refine_lens_hidden_trg_entType_div','uri',obj.o_datatype);
    setAttr('refine_lens_hidden_trg_entType_div','label',obj.o_datatype_label);

    datasetClick(document.getElementById('refine_lens_hidden_src_div'));
    datasetClick(document.getElementById('refine_lens_hidden_trg_div'));

    setAttr('refine_lens_hidden_src_div','uri','');
    setAttr('refine_lens_hidden_src_div','label','');

    setAttr('refine_lens_hidden_trg_div','uri','');
    setAttr('refine_lens_hidden_trg_div','label','');

    var ancestorType = "entity-list";

    selectionClick(document.getElementById('refine_lens_hidden_src_entType_div'), ancestorType);
    selectionClick(document.getElementById('refine_lens_hidden_trg_entType_div'), ancestorType);

    setAttr('refine_lens_hidden_src_entType_div','uri','');
    setAttr('refine_lens_hidden_src_entType_div','label','');

    setAttr('refine_lens_hidden_trg_entType_div','uri','');
    setAttr('refine_lens_hidden_trg_entType_div','label','');

    $('#refine_lens_button-src-entity-type-col').hide();
    $('#refine_lens_button-trg-entity-type-col').hide();
    $('#refine_lens_button-src-col').hide();
    $('#refine_lens_button-trg-col').hide();
}


function create_lens_activate()
{
   var rq_uri = $('#creation_lens_selected_RQ').attr('uri');

    $('#creation_linkset_correspondence_row').html('');
    $('#lens_creation_linkset_col').hide();
    $('#lens_creation_lens_col').hide();
    $('#lens_creation_linkset_col_diff').hide();
    $('#lens_creation_lens_col_diff').hide();

    //   $('#lens_creation_message_col').html('');
    refresh_create_lens();
    $('#lens_inspect_panel_body').show();
    $('#lens_creation_row').show();
    $('#lens_refine_row').hide();

   $('#creation_lens_linkset_selection_col').html('Loading...');
   $.get('/getgraphsperrqtype',data={'rq_uri': rq_uri,
                          'type': 'linkset',
                          'template': 'list_group.html'},function(data)
   {
     $('#creation_lens_linkset_selection_col').html(data);
       var ul = document.getElementById('creation_lens_linkset_selection_col');
       var a = ul.getElementsByTagName('a');
       var num = ('0000' + String(a.length)).substr(-4);
       $('#lens_lkst_counter').html(num);

     // set actions after clicking a graph in the list
     $('#creation_lens_linkset_selection_col a').on('click',function()
      { selectListItem(this); });

    // Fill in source and target
     $('#creation_lens_linkset_selection_source_col').html(data);
       $('#lens_lkst_src_counter').html(num);
     // set actions after clicking a graph in the list
     $('#creation_lens_linkset_selection_source_col a').on('click',function()
      { selectListItemUniqueDeselect(this, 'creation_lens_linkset_selection_source_col') });

     $('#creation_lens_linkset_selection_target_col').html(data);
       $('#lens_lkst_trg_counter').html(num);
     // set actions after clicking a graph in the list
     $('#creation_lens_linkset_selection_target_col a').on('click',function()
      { selectListItemUniqueDeselect(this, 'creation_lens_linkset_selection_target_col') });

   });

   $('#creation_lens_lens_selection_col').html('Loading...');
   $.get('/getgraphsperrqtype',data={'rq_uri': rq_uri,
                          'type': 'lens',
                          'template': 'list_group.html'},function(data)
   {
     $('#creation_lens_lens_selection_col').html(data);
       var ul = document.getElementById('creation_lens_lens_selection_col');
       var a = ul.getElementsByTagName('a');
       var num = ('0000' + String(a.length)).substr(-4);
       $('#lens_lens_counter').html(num);

     // set actions after clicking a graph in the list
     $('#creation_lens_lens_selection_col a').on('click',function()
      { selectListItem(this); });

    // Fill in source and target
     $('#creation_lens_lens_selection_source_col').html(data);
       $('#lens_lens_src_counter').html(num);
     // set actions after clicking a graph in the list
     $('#creation_lens_lens_selection_source_col a').on('click',function()
      { selectListItemUniqueDeselect(this, 'creation_lens_lens_selection_source_col') });

     $('#creation_lens_lens_selection_target_col').html(data);
       $('#lens_lens_trg_counter').html(num);
     // set actions after clicking a graph in the list
     $('#creation_lens_lens_selection_target_col a').on('click',function()
      { selectListItemUniqueDeselect(this, 'creation_lens_lens_selection_target_col') });

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

  $('#lens_creation_linkset_col_diff').hide();
  $('#lens_creation_linkset_col').show();
  $('#lens_creation_lens_col_diff').hide();
  $('#lens_creation_lens_col').show();

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
      description = 'The operator TRANSITIVE requires a source and a target alignments as its arguments, then calculates correspondences between entities in the first and the latter that are linked through a common entity.';
      $('#lens_creation_linkset_col_diff').show();
      $('#lens_creation_linkset_col').hide();
      $('#lens_creation_lens_col_diff').show();
      $('#lens_creation_lens_col').hide();
  }
  else if (operator_label == 'difference')
  {
      description = 'The operator DIFFERENCE requires a source and a target alignments as its arguments, then calculates correspondences that exists in the first but not in the latter.';
      $('#lens_creation_linkset_col_diff').show();
      $('#lens_creation_linkset_col').hide();
      $('#lens_creation_lens_col_diff').show();
      $('#lens_creation_lens_col').hide();
  }
  $('#selected_operator_desc').html(description);

}


function createLensClick()
{
    var rq_uri = $('#creation_lens_selected_RQ').attr('uri');
    var operator = $('#selected_operator').attr('label');
    var graphs = [];
    var source = '';
    var target = '';

    if ((operator == 'difference') || (operator == 'transitive'))
    {
        var elems_linkset = selectedElemsInGroupList('creation_lens_linkset_selection_source_col');
        var elems_lens = selectedElemsInGroupList('creation_lens_lens_selection_source_col');
        if ((elems_linkset.length > 0) && (elems_lens.length == 0))
        {  source = $(elems_linkset[0]).attr('uri');
        }
        else if ((elems_linkset.length == 0) && (elems_lens.length > 0))
        {  source = $(elems_lens[0]).attr('uri');
        }
        var elems_linkset = selectedElemsInGroupList('creation_lens_linkset_selection_target_col');
        var elems_lens = selectedElemsInGroupList('creation_lens_lens_selection_target_col');
        if ((elems_linkset.length > 0) && (elems_lens.length == 0))
        {  target = $(elems_linkset[0]).attr('uri');
        }
        else if ((elems_linkset.length == 0) && (elems_lens.length > 0))
        {  target = $(elems_lens[0]).attr('uri');
        }
    }
    else
    {
        var elems = selectedElemsInGroupList('creation_lens_linkset_selection_col');
        var i;
        for (i = 0; i < elems.length; i++) {
          graphs.push($(elems[i]).attr('uri'));
        }
        elems = selectedElemsInGroupList('creation_lens_lens_selection_col');
        var i;
        for (i = 0; i < elems.length; i++) {
          graphs.push($(elems[i]).attr('uri'));
        }
    }

    if ( ( ( !((operator == 'difference') || (operator == 'transitive')) && (graphs.length > 0) ) ||
           ( ((operator == 'difference') || (operator == 'transitive')) && (source != '') && (target != '')) ) &&
         ($('#selected_operator').attr('label')))
    {
        var specs = {'rq_uri': rq_uri,
                    'graphs[]': graphs,
                    'subjects_target': source,
                    'objects_target': target,
                    'operator': $('#selected_operator').attr('label')};

        var message = "EXECUTING YOUR LENS SPECS.<br/>PLEASE WAIT UNTIL THE COMPLETION OF YOUR EXECUTION";
        $('#lens_creation_message_col').html(addNote(message,cl='warning'));
        loadingGif(document.getElementById('lens_creation_message_col'), 2);


        // call function that creates the linkset
        $.get('/createLens', specs, function(data)
        {
            var obj = JSON.parse(data);
            $('#lens_creation_message_col').html(addNote(obj.message, cl='info'));
            loadingGif(document.getElementById('lens_creation_message_col'), 2, show=false);

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


function refineLensClick()
{
    var reducer = ''; intermediate = '';
    if ($('#refine_lens_selected_meth').attr('uri') != 'intermediate')
     {   reducer = $('#refine_lens_selected_int_red_graph').attr('uri'); }
    else
     {   intermediate = $('#refine_lens_selected_int_red_graph').attr('uri'); }

  $('#lens_refine_message_col').html("");

  var srcDict = {};
  if (($('#refine_lens_src_selected_graph').attr('uri')) &&
     ($('#refine_lens_src_selected_pred').attr('uri')) &&
     ($('#refine_lens_src_selected_entity-type').attr('uri'))  )
  {
     srcDict = {'graph': $('#refine_lens_src_selected_graph').attr('uri'),
                'aligns': $('#refine_lens_src_selected_pred').attr('uri'),
                'entity_datatye': $('#refine_lens_src_selected_entity-type').attr('uri')};
  }

  var trgDict = {};
  if (($('#refine_lens_trg_selected_graph').attr('uri')) &&
      ( $('#refine_lens_trg_selected_pred').attr('uri') ||
       ($('#refine_lens_selected_meth').attr('uri') == 'embededAlignment')) &&
     ($('#refine_lens_trg_selected_entity-type').attr('uri')) )
  {
     trgDict = {'graph': $('#refine_lens_trg_selected_graph').attr('uri'),
                'aligns': $('#refine_lens_trg_selected_pred').attr('uri'),
                'entity_datatye': $('#refine_lens_trg_selected_entity-type').attr('uri')};
  }

  var linkset = '';
  var elems = selectedElemsInGroupList('inspect_lens_lens_selection_col');
  if (elems.length > 0) // it should have only one selected
  {
    linkset = $(elems[0]).attr('uri');
  }

 if ((Object.keys(srcDict).length) &&
        (Object.keys(trgDict).length) &&
        ($('#refine_lens_selected_meth').attr('uri')) &&
        ($('#refine_lens_selected_meth').attr('uri') != 'intermediate' || intermediate) &&
      (linkset) &&
        ($('#refine_lens_selected_meth').attr('uri') != 'approxNbrSim' ||
            ($('#refine_lens_approx_delta').val() && $('#refine_lens_approx_num_type').val() ))
      )
  {

      var specs = {
        'rq_uri': $('#creation_lens_selected_RQ').attr('uri'),
        'alignment_uri': linkset,

        'src_graph': $('#refine_lens_src_selected_graph').attr('uri'),
        'src_aligns': $('#refine_lens_src_selected_pred').attr('uri'),
        'src_entity_datatye': $('#refine_lens_src_selected_entity-type').attr('uri'),
        'src_reducer': reducer,

        'trg_graph': $('#refine_lens_trg_selected_graph').attr('uri'),
        'trg_aligns': $('#refine_lens_trg_selected_pred').attr('uri'),
        'trg_entity_datatye': $('#refine_lens_trg_selected_entity-type').attr('uri'),
        'trg_reducer': reducer,

        'mechanism': $('#refine_lens_selected_meth').attr('uri'),

        'intermediate_graph': intermediate,

        'delta': $('#refine_lens_approx_delta').val() ,
        'numeric_approx_type': $('#refine_lens_approx_num_type').val()
      }

      var message = "EXECUTING YOUR LINKSET SPECS.</br>PLEASE WAIT UNTIL THE COMPLETION OF YOUR EXECUTION";
      $('#lens_refine_message_col').html(addNote(message,cl='warning'));
      loadingGif(document.getElementById('lens_refine_message_col'), 2);

      // call function that creates the linkset
      // HERE!!!!
      $.get('/refineAlignment', specs, function(data)
      {
            var obj = JSON.parse(data);
            $('#lens_refine_message_col').html(addNote(obj.message,cl='info'));
            loadingGif(document.getElementById('lens_refine_message_col'), 2, show=false);
      });

  }
  else {
    $('#lens_refine_message_col').html(addNote(missing_feature));
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


function deleteLensClick()
{
    var rq_uri = $('#creation_lens_selected_RQ').attr('uri');
    var lens = '';
    var elems = selectedElemsInGroupList('inspect_lens_lens_selection_col');
    if (elems.length > 0) // if any element is selected
    {
        lens = $(elems[0]).attr('uri');  // it should have only one selected
        //alert(lens);
        var message = "Checking for lens dependencies...";
        $('#lens_edit_message_col').html(addNote(message,cl='warning'));
        loadingGif(document.getElementById('lens_edit_message_col'), 2);

        // call function that creates the linkset
        $.get('/deleteLens', data={'rq_uri':rq_uri, 'lens_uri':lens, 'mode':'check'}, function(data)
        {
            var obj = JSON.parse(data);
            if (obj.message == 'OK')
            {   var test = confirm("Delete the lens?");
                if (test)
                {
                    var message = "Deleting Lens...";
                    $('#lens_edit_message_col').html(addNote(message,cl='warning'));

                    $.get('/deleteLens', data={'rq_uri':rq_uri, 'lens_uri':lens, 'mode':'delete'}, function(data)
                    {
                        var obj = JSON.parse(data);
                        if (obj.result == 'OK')
                        {   $('#btn_edit_lens').click();
                            $('#lens_edit_message_col').html(addNote(obj.message,cl='info')); }
                        else
                        {    $('#lens_edit_message_col').html(addNote(obj.message)); }

                        loadingGif(document.getElementById('lens_edit_message_col'), 2, show=false);
                    });
                }
                else
                {   $('#lens_edit_message_col').html('');
                    loadingGif(document.getElementById('lens_edit_message_col'), 2, show=false);
                }
            }
            else if (obj.message == 'Check Dependencies')
            {
                $('#lens_edit_message_col').html(addNote(obj.result));
                loadingGif(document.getElementById('lens_edit_message_col'), 2, show=false);
            }
            else
            {
                $('#lens_edit_message_col').html(addNote(obj.message));
                loadingGif(document.getElementById('lens_edit_message_col'), 2, show=false);
            }
        });
    }
}


///////////////////////////////////////////////////////////////////////////////
// Functions called at onclick of the buttons in clustersCreation.html
///////////////////////////////////////////////////////////////////////////////

function create_clusters_activate()
{
    // cleaning ...
    $('#creation_cluster_predicates_col').html('');
    $('#creation_cluster_selected_predicates_group').html('');
    $('#cluster_creation_message_col').html('');
    $('#cluster_creation_save_message_col').html('');
    $('#creation_cluster_results_row').hide();
    chronoReset();

    var rq_uri = $('#creation_cluster_selected_RQ').attr('uri');

    // loading...
    cluster_load_datasets(rq_uri);
    //cluster_load_datasets_predicates(rq_uri);

//    view_load_linkesets_lenses(rq_uri);
}

function inspect_clusters_activate(mode="inspect")
{
  var rq_uri = $('#creation_cluster_selected_RQ').attr('uri');
  chronoReset();

  if (rq_uri)
  {

    if (mode == 'inspect')
    {
        $('#inspect_cluster_heading').show();
        $('#edit_cluster_heading').hide();
    }
    else //edit
    {
        $('#inspect_cluster_heading').hide();
        $('#edit_cluster_heading').show();
        enableButton('deleteClusterButton', enable=false);
        enableButton('editLabelClusterButton', enable=false);
    }

    $('#cluster_edit_message_col').html("");

    $('#inspect_clusters_details_col').html('');
    $('#inspect_clusters_selection_col').html('Loading...');
    // Load into div all the existing views for a certain research question
    $.get('/getgraphsperrqtype',
                  data={'rq_uri': rq_uri,
                        'type': 'cluster',
                        'template': 'list_group.html'},
                  function(data)
    {
      $('#inspect_clusters_selection_col').html(data);

      // set actions after clicking a graph in the list
      $('#inspect_clusters_selection_col a').on('click',function()
       {
          if (selectListItemUnique(this, 'inspect_clusters_selection_col'))
          {
            $('#cluster_creation_message_col').html("");
            $('#cluster_creation_message_col').html("");
            $('#cluster_creation_save_message_col').html("");
            $('#creation_cluster_selected_predicates_group').html("");
            var cluster_uri = $(this).attr('uri');

              // load the panel for correspondences details
              $('#inspect_clusters_details_col').html('Loading...');
              $.get('/getclusterdetails',data={'rq_uri': rq_uri,
                                            'cluster_uri': cluster_uri},function(data)
              {
                var obj = JSON.parse(data);

                $('#inspect_clusters_details_col').html(obj.details);

                if (mode == 'inspect')
                {
                    //show the creation-panels containing the linksets/lenses
                    //and the datasets and properties to be selected
                    //create_views_activate( function(){ alert('sync'); } );

                    //alert('after');
                    $('#creation_cluster_row').show();
                    $('#creation_cluster_filter_row').show();

                    cluster_load_datasets(rq_uri);
//                    cluster_load_datasets_predicates(rq_uri, obj.list_pred);
//                    cluster_load_linkesets_lenses(rq_uri, obj.cluster_lens);
                }
                else if (mode == 'edit')
                {
                    $('#creation_cluster_row').hide();
                    $('#creation_cluster_filter_row').hide();
                    enableButton('deleteClusterButton');
                    enableButton('editLabelClusterButton');
                }

              });

           $('#creation_cluster_results_row').hide();
           $("#collapse_cluster_filter").collapse("hide");

          }
        });
    });

  }
}


function cluster_load_datasets(rq_uri)
{
// Load into div the selected datasets for a certain research question
     $('#creation_cluster_dataset_col').html('Loading...');
     $.get('/getgraphsentitytypes',data={'rq_uri': rq_uri, 'mode': 'cluster'},function(data)
     {
       $('#creation_cluster_dataset_col').html(data);

       // when a dataset from the list is selected, its list of predicates will be loaded
       $('#creation_cluster_dataset_col li').on('click',function()
       {
          if (selectListItemUnique(this, 'creation_cluster_dataset_col'))
          {
                cluster_load_predicates(rq_uri, this);
          }
       });
     });

}

function cluster_load_predicates(rq_uri, source)
{
    var graph_uri = $(source).attr('uri');
    var graph_label = $(source).attr('label');
    var type_uri = $(source).attr('type_uri');
    var type_label = $(source).attr('type_label');
    var total = $(source).attr('total');
    var propPath = $('#creation_cluster_predicates_col').attr('accumPath');

      // Exhibit a waiting message for the user to know loading time might be long.
      $('#creation_cluster_predicates_col').html('Loading...');
      if (propPath != '') type_uri = '';
      // get the distinct predicates and example values of a graph into a list group
      $.get('/getpredicates',data={'dataset_uri': graph_uri,
                                   'type': type_uri,
                                   'propPath': propPath,
                                   'total': total},function(data)
      {
          // load the rendered template into the column #creation_view_predicates_col
          var obj = JSON.parse(data);
          if (obj.message == 'OK') {
               $('#creation_cluster_predicates_col').html(obj.result);
               var ul = document.getElementById('creation_cluster_predicates_col');
               var li = ul.getElementsByTagName('li');
               var num = ('0000' + String(li.length)).substr(-4);
               $('#cluster_pred_counter').html(num);
          }
          else
                $('#creation_cluster_predicates_col').html(obj.message);

          // set actions after clicking one of the predicates
          $('#creation_cluster_predicates_col li').on('click',function()
          {
            var pred_uri = $(this).attr('uri');
            var pred_label = $(this).attr('label');
            if ($('#creation_cluster_predicates_col').attr('accumPath') != '')
            {  pred_uri = $('#creation_cluster_predicates_col').attr('accumPath') + '/' + pred_uri;
               pred_label = $('#creation_cluster_predicates_col').attr('accumPathLabel') + '/' + pred_label
            }
            var checkPropPath = document.getElementById('cluster_enable_prop_path');
            if (($(this).attr('obj_type') == 'uri') && (checkPropPath.checked))
            {
              setAttr('creation_cluster_predicates_col','accumPath',pred_uri);
              setAttr('creation_cluster_predicates_col','accumPathLabel',pred_label);
              cluster_load_predicates(rq_uri, source);
            }
            else
            {
                var i;
                var check = false;
                var elem = document.getElementById('creation_cluster_selected_predicates_group');
                if (elem) {
                    var elems = elem.getElementsByClassName('list-group-item');
                    for (i = 0; i < elems.length; i++) {
                        if ( ($(elems[i]).attr('pred_uri') == pred_uri)
                                 && ($(elems[i]).attr('graph_uri') == graph_uri) )
                        {
                          check = true;
                          break;
                        }
                    }
                    if (!check) {
                       var item = '<li class="list-group-item" pred_uri="' + pred_uri
                                + '" graph_uri="' + graph_uri
                                + '" type_uri="' + type_uri
                                + '" onclick= "this.parentElement.removeChild(this);"'
                                + '><span class="list-group-item-heading"><b>'
                                + graph_label + ' | ' + type_label + '</b>: ' + pred_label + '</span></li>';
                       $('#creation_cluster_selected_predicates_group').prepend(item);
                    }
                    setAttr('creation_cluster_predicates_col','accumPath','');
                    setAttr('creation_cluster_predicates_col','accumPathLabel','');
                }
            }
          });
      });

}

function createClusterClick()
{
    $('#cluster_creation_message_col').html("");

    var rq_uri = $('#creation_cluster_selected_RQ').attr('uri');

    var cluster_specs = []
    var elem = document.getElementById('creation_cluster_selected_predicates_group');
    if (elem) {
        elems = elem.getElementsByClassName('list-group-item');
    }
    var dict = {};
    for (i = 0; i < elems.length; i++) {

        var entityType = $(elems[i]).attr('type_uri');
        if (!entityType) {entityType = 'no_type'};
        dict = {'ds': $(elems[i]).attr('graph_uri'),
                'type': entityType,
                'att': $(elems[i]).attr('pred_uri').replace('>',"").replace('<',"") };
        cluster_specs.push( JSON.stringify(dict));
    }

     if (mode=='check')
     {   var message_col = 'cluster_creation_message_col'; }
     else
     {   var message_col = 'cluster_creation_save_message_col'; }

    if (cluster_specs.length > 0)
    {
     var specs = {'mode': mode,
                  'rq_uri': rq_uri,
                  'cluster_specs[]': cluster_specs};

     chronoReset();
     $('#'+message_col).html(addNote('The proposed cluster is being processed',cl='warning'));
     loadingGif(document.getElementById(message_col), 2);

     $.get('/createClusterContraint', specs, function(data)
     {
         var obj = JSON.parse(data);
         //{"metadata": metadata, "query": '', "table": []}
//         $('#queryView').val(obj.query);
         $('#creation_cluster_results_row').show();

         if (obj.reference)
             $('#'+message_col).html(addNote(obj.message,cl='info'));
         else
             $('#'+message_col).html(addNote(obj.message,cl='warning'));

         loadingGif(document.getElementById(message_col), 2, show = false);

//         if (obj.sparql_issue)
//         {   var message = 'We cannot run the query because at least one non-optional property is required for each dataset in the select clause.'
//             $('#'+message_col).html(addNote(message,cl='warning'));
//             enableButton('view_run_button', enable=false);
//             loadingGif(document.getElementById(message_col), 2, show = false);
//         }
//         else
//         {   //enableButton('view_run_button');
//             $('#'+message_col).html(addNote(obj.metadata.message,cl='info'));
//             loadingGif(document.getElementById(message_col), 2, show = false);
////             runViewClick();
//         }

     });
    }
    else {
        $('#'+message_col).html(addNote(missing_feature));
    }
}

///////////////////////////////////////////////////////////////////////////////
// Functions called at onclick of the buttons in viewsCreation.html
///////////////////////////////////////////////////////////////////////////////


function create_views_activate()
{
    // cleaning ...
    $('#creation_view_predicates_col').html('');
    $('#creation_view_selected_predicates_group').html('');
    $('#view_creation_message_col').html('');
    $('#view_creation_save_message_col').html('');
    $('#creation_view_results_row').hide();
    chronoReset();

    var rq_uri = $('#creation_view_selected_RQ').attr('uri');

    // loading...
    view_load_datasets_predicates(rq_uri);

    view_load_linkesets_lenses(rq_uri);
}


function view_load_datasets_predicates(rq_uri, view_filters=null)
{
// Load into div the selected datasets for a certain research question
     $('#creation_view_dataset_col').html('Loading...');
     $.get('/getgraphsentitytypes',data={'rq_uri': rq_uri, 'mode': 'view'},function(data)
     {
       $('#creation_view_dataset_col').html(data);

       // when a dataset from the list is selected, its list of predicates will be loaded
       $('#creation_view_dataset_col li').on('click',function()
       {
          var graph_uri = $(this).attr('uri');
          var graph_label = $(this).attr('label');
          var type_uri = $(this).attr('type_uri');
          var type_label = $(this).attr('type_label');
          var total = $(this).attr('total');

          if (selectListItemUnique(this, 'creation_view_dataset_col'))
          {
              // Exhibit a waiting message for the user to know loading time might be long.
              $('#creation_view_predicates_col').html('Loading...');
              // get the distinct predicates and example values of a graph into a list group
              $.get('/getpredicates',data={'dataset_uri': graph_uri, 'type': type_uri, 'total': total},function(data)
              {
                  // load the rendered template into the column #creation_view_predicates_col
                  var obj = JSON.parse(data);
                  if (obj.message == 'OK') {
                       $('#creation_view_predicates_col').html(obj.result);
                       var ul = document.getElementById('creation_view_predicates_col');
                       var li = ul.getElementsByTagName('li');
                       var num = ('0000' + String(li.length)).substr(-4);
                       $('#view_pred_counter').html(num);
                  }
                  else
                        $('#creation_view_predicates_col').html(obj.message);

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
                            {
                              check = true;
                              break;
                            }
                        }
                        if (!check) {
                           var item = '<li class="list-group-item" pred_uri="' + pred_uri
                                    + '" graph_uri="' + graph_uri
                                    + '" type_uri="' + type_uri
                                    + '" onclick= "this.parentElement.removeChild(this);"'
                                    + '><span class="list-group-item-heading"><b>'
                                    + graph_label + ' | ' + type_label + '</b>: ' + pred_label + '</span></li>';
                           $('#creation_view_selected_predicates_group').prepend(item);
                        }
                    }
                  });
              });
          }

       });
     });

     if ((view_filters) && (view_filters.length > 0))
     {
        $('#creation_view_registered_predicates_group').html("");
        //var view_filters = obj.list_pred
        for (i = 0; i < view_filters.length; i++) {
              $('#creation_view_selected_predicates_group').prepend(view_filters[i]);
        }
     }
}


function view_load_linkesets_lenses(rq_uri, view_lens=null)
{
  $('#creation_view_linkset_col').html('Loading...');
     $.get('/getgraphsperrqtype',data={'rq_uri': rq_uri,
                            'type': 'linkset',
                            'template': 'list_group.html'},function(data)
     {
       $('#creation_view_linkset_col').html(data);
       var ul = document.getElementById('creation_view_linkset_col');
       var a = ul.getElementsByTagName('a');
       var num = ('0000' + String(a.length)).substr(-4);
       $('#view_linkset_counter').html(num);

        if ((view_lens) && (view_lens.length > 0))
        {
            // assigning the selected graphs and properties
            var i, elem, elems;
            elem = document.getElementById('creation_view_linkset_col');
//            console.log(elem);
            if (elem) {
                elems = elem.getElementsByClassName('list-group-item');
                for (i = 0; i < elems.length; i++) {
                    uri = $(elems[i]).attr('uri');
                    if (view_lens.includes(uri))
                    {
                        selectListItem(elems[i]);
                    }
                }
            }
        }

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
       var ul = document.getElementById('creation_view_lens_col');
       var a = ul.getElementsByTagName('a');
       var num = ('0000' + String(a.length)).substr(-4);
       $('#view_lens_counter').html(num);

       if ((view_lens) && (view_lens.length > 0))
       {
            elem = document.getElementById('creation_view_lens_col');
            if (elem) {
                elems = elem.getElementsByClassName('list-group-item');
                for (i = 0; i < elems.length; i++) {
                    uri = $(elems[i]).attr('uri');
                    if (view_lens.includes(uri))
                    {
                        selectListItem(elems[i]);
                    }
                }
            }
       }

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
  chronoReset();

  if (rq_uri)
  {

    if (mode == 'inspect')
    {
        $('#inspect_view_heading').show();
        $('#edit_view_heading').hide();
    }
    else //edit
    {
        $('#inspect_view_heading').hide();
        $('#edit_view_heading').show();
        enableButton('deleteViewButton', enable=false);
        enableButton('editLabelViewButton', enable=false);
    }

    $('#view_edit_message_col').html("");

    $('#inspect_views_details_col').html('');
    $('#inspect_views_selection_col').html('Loading...');
    // Load into div all the existing views for a certain research question
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
            $('#view_creation_message_col').html("");
            $('#view_creation_save_message_col').html("");
            $('#creation_view_selected_predicates_group').html("");
            var view_uri = $(this).attr('uri');

              // load the panel for correspondences details
              $('#inspect_views_details_col').html('Loading...');
              $.get('/getviewdetails',data={'rq_uri': rq_uri,
                                            'view_uri': view_uri},function(data)
              {
                var obj = JSON.parse(data);

                $('#inspect_views_details_col').html(obj.details);

                if (mode == 'inspect')
                {
                    //show the creation-panels containing the linksets/lenses
                    //and the datasets and properties to be selected
                    //create_views_activate( function(){ alert('sync'); } );

                    //alert('after');
                    $('#creation_view_row').show();
                    $('#creation_view_filter_row').show();

                    view_load_datasets_predicates(rq_uri, obj.list_pred);
                    view_load_linkesets_lenses(rq_uri, obj.view_lens);
                }
                else if (mode == 'edit')
                {
                    $('#creation_view_row').hide();
                    $('#creation_view_filter_row').hide();
                    enableButton('deleteViewButton');
                    enableButton('editLabelViewButton');
                }

              });

           $('#creation_view_results_row').hide();
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
    $('#view_run_message_col').html("");
    $('#queryView').val("");
    $('#views-results').html("");

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

        var entityType = $(elems[i]).attr('type_uri');
        if (!entityType) {entityType = 'no_type'};
        dict = {'ds': $(elems[i]).attr('graph_uri'),
                'type': entityType,
                'att': $(elems[i]).attr('pred_uri').replace('>',"").replace('<',"") };
        view_filter.push( JSON.stringify(dict));
    }

     if (mode=='check')
     {   var message_col = 'view_creation_message_col'; }
     else
     {   var message_col = 'view_creation_save_message_col'; }

    if ((view_lens.length > 0) && (view_filter.length > 0))
    {
     var specs = {'mode': mode,
                  'rq_uri': rq_uri,
                  'view_lens[]': view_lens,
                  'view_filter[]': view_filter};

     chronoReset();
     $('#'+message_col).html(addNote('The proposed view is being processed',cl='warning'));
     loadingGif(document.getElementById(message_col), 2);

     $.get('/createView', specs, function(data)
     {
         var obj = JSON.parse(data);
         //{"metadata": metadata, "query": '', "table": []}
         $('#queryView').val(obj.query);
         $('#creation_view_results_row').show();

         if (obj.sparql_issue)
         {   var message = 'We cannot run the query because at least one non-optional property is required for each dataset in the select clause.'
             $('#'+message_col).html(addNote(message,cl='warning'));
             enableButton('view_run_button', enable=false);
             loadingGif(document.getElementById(message_col), 2, show = false);
         }
         else
         {   enableButton('view_run_button');
             $('#'+message_col).html(addNote(obj.metadata.message,cl='info'));
             loadingGif(document.getElementById(message_col), 2, show = false);
             runViewClick();
         }

     });
    }
    else {
        $('#'+message_col).html(addNote(missing_feature));
    }
}


function deleteViewClick()
{
    var rq_uri = $('#creation_view_selected_RQ').attr('uri');
    var view = '';
    var elems = selectedElemsInGroupList('inspect_views_selection_col');
    if (elems.length > 0) // if any element is selected
    {
        view = $(elems[0]).attr('uri');  // it should have only one selected
        //var message = "Checking for linkset dependencies...";
        //$('#linkset_edit_message_col').html(addNote(message,cl='warning'));
        //loadingGif(document.getElementById('linkset_edit_message_col'), 2);

        var test = confirm("Delete the view?");
        if (test)
        {
            var message = "Deleting View...";
            $('#view_edit_message_col').html(addNote(message,cl='warning'));
            loadingGif(document.getElementById('view_edit_message_col'), 2);
            $.get('/deleteView', data={'rq_uri':rq_uri, 'view_uri':view, 'mode':'delete'}, function(data)
            {
                var obj = JSON.parse(data);
                if (obj.result == 'OK')
                {   $('#btn_edit_view').click();
                    $('#view_edit_message_col').html(addNote(obj.message,cl='info')); }
                else
                {    $('#view_edit_message_col').html(addNote(obj.message)); }

                loadingGif(document.getElementById('view_edit_message_col'), 2, show=false);
            });
        }
    }
}


function runViewClick()
{
  //$('#view_creation_message_col').html("");
  var query = $('#queryView').val();
  $('#views-results').html("");

  $('#view_run_message_col').html(addNote('The query is running.',cl='warning'));
  loadingGif(document.getElementById('view_run_message_col'), 2);

  $.get('/sparql',data={'query': query}, function(data)
  {
    var obj = JSON.parse(data);
    $('#views-results').html(obj.result);
    $('#view_run_message_col').html(addNote(obj.message,cl='info'));
    loadingGif(document.getElementById('view_run_message_col'), 2, show = false);
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
          var btn2 = document.getElementById('btn_create_idea');
          update_idea_enable(rq_uri);
          overview_idea_enable(rq_uri);
          if ( selectedButton(btn) )
          { $('#overview_idea_row').hide();
          } else if ( selectedButton(btn2))
          { $('#overview_idea_row').hide();
          } else
          { $('#creation_idea_update_col').hide(); }
          btn = null;
          break;
      case 'view':
          enableButtons(document.getElementById('creation_views_buttons_col'));
          refresh_create_view();
          var btn = document.getElementById('btn_inspect_view');
          break;
      case 'cluster':
          enableButtons(document.getElementById('creation_clusters_buttons_col'));
          //refresh_create_cluster();
          var btn = document.getElementById('btn_inspect_cluster');
          break;
      case 'dataset':
          inspect_dataset_activate(rq_uri);
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

  target = 'creation_cluster_selected_RQ';
  setAttr(target,'uri',rq_uri);
  setAttr(target,'label',rq_label);
  setAttr(target,'style','background-color:lightblue');
  $('#'+target).html(rq_label);

  target = 'creation_idea_selected_RQ';
  setAttr(target,'uri',rq_uri);
  setAttr(target,'label',rq_label);
  setAttr(target,'style','background-color:lightblue');
  $('#'+target).html(rq_label);

  target = 'dataset_inspection_selected_RQ';
  setAttr(target,'uri',rq_uri);
  setAttr(target,'label',rq_label);
  setAttr(target,'style','background-color:lightblue');
  $('#'+target).html(rq_label);

//  if (btn)  //inital button selected
//  {  btn.onclick();
//  }
}

function intRedGraphClick(th)
{
    list = findAncestor(th,'graph-list');

    // get the graph uri and label from the clicked dataset
    var graph_uri = $(th).attr('uri');
    var graph_label = $(th).attr('label');

    // Attribute the uri of the selected graph to the div
    // where the name/label is displayed
    var targetTxt = $(list).attr('targetTxt');
    setAttr(targetTxt,'uri',graph_uri);
    $('#'+targetTxt).html(graph_label.toUpperCase());
    setAttr(targetTxt,'style','background-color:lightblue; scroll: both; overflow: auto');
    //display: inline-block;');
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

    // get the graph uri and label from the clicked dataset
    var graph_uri = $(th).attr('uri');
    var graph_label = $(th).attr('label');

    // Attribute the uri of the selected graph to the div
    // where the name/label is displayed
    var targetTxt = $(list).attr('targetTxt');
    setAttr(targetTxt,'uri',graph_uri);
    setAttr(targetTxt,'graph_uri',graph_uri);
    $('#'+targetTxt).html(graph_label.toUpperCase());
    setAttr(targetTxt,'style','background-color:lightblue;');

    var button = $(list).attr('targetBtn');
    if (button)
    {
        setAttr(button,'graph_uri',graph_uri);
        var targetHidden = $(list).attr('targetHidden');
        // if there is not entity type settled via the targetHidden
        // then load the button
        var elem = document.getElementById(targetHidden)
        if ((!elem) || ($('#'+targetHidden).attr('uri') == ''))
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
}


// Function fired onclick of a option from a list
// it reads from the ancestor-element of a certain class
// the element in which to copy the chosen item through the tag 'targetTxt'
function selectionClick(th, ancestorType)
{
    list = findAncestor(th, ancestorType);

    var targetTxt = $(list).attr('targetTxt');
    var label = $(th).attr('label');
    var listCol = $(list).attr('targetList');
    var checkPropPath = document.getElementById($(list).attr('propPathCheckBok'));

    // Attributes the uri of the selected entity to the
    // corresponding div where the label is displayed
    // and changes its background color

    // it is not the list of predicates, then just attribute
    // the uri and label to the corresponding divs
    if ((ancestorType != 'pred-list') || !(checkPropPath.checked))
    {   setAttr(targetTxt,'uri', $(th).attr('uri') );
        $('#'+targetTxt).html( label );
    }
    // however, if the ancestor is list of predicates, we need to consider the
    // cumulative attribution of values in a property path
    else
    {
        if ( ($('#'+targetTxt).html() == 'Select a Property + <span style="color:blue"><strong> example value </strong></span>') )
        {
            setAttr(targetTxt,'uri', $(th).attr('uri') );
            $('#'+targetTxt).html( label );
            var propPath = $(th).attr('uri');
        }
        else if ($('#'+listCol).attr('propPath')!='disabled')
        {
            var new_text = $('#'+targetTxt).html() + ' / ' + label;
            var propPath = $('#'+targetTxt).attr('uri') + '/' + $(th).attr('uri');
            setAttr(targetTxt,'uri', propPath );
            $('#'+targetTxt).html( new_text );
        }
        else //replace the last property in the path
        {
            var old_text = $('#'+targetTxt).html();
            var old_path = $('#'+targetTxt).attr('uri');
            var index =  old_text.lastIndexOf(" / ");
            var new_text = old_text.substring(0, index) + ' / ' + label;
            index =  old_path.lastIndexOf("/<");
            var propPath = old_path.substring(0, index) + '/' + $(th).attr('uri');
            setAttr(targetTxt,'uri', propPath );
            $('#'+targetTxt).html( new_text );
        }
    }
    setAttr(targetTxt,'style', 'background-color:lightblue');

    // If a tag optional is provided, change the color of the label accordingly
    var optional = $(th).attr('optional');
    if (optional)
    {
        if (optional == 'true')
        {    label = '<strong><span style="color:red">'+label+'</span></strong>' }
        else
        {    label = '<strong><span style="color:blue">'+label+'</span></strong>' }
    }

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

    var graph_uri = $(list).attr('graph_uri');
    if (listCol)
    {
        //alert($('#'+listCol).attr('propPath'));
        if (ancestorType != 'pred-list')
        {
            setAttr(listCol,'graph_uri',graph_uri);
            // clean previously selected entity type
            targetTxt = $('#'+listCol).attr('targetTxt');

            setAttr(targetTxt,'uri','');
            $('#'+targetTxt).html('Select a Property + <span style="color:blue"><strong> example value </strong></span>');
            setAttr(targetTxt,'style','background-color:none');

            // get the distinct predicates and example values of a graph into a list group
            $('#'+listCol).html('Loading...');
//            alert('before')

            //TODO: Improve... to make it work for dataset inspection and enrichment
            var listCol2 = $(list).attr('targetList2');
            var listCol3 = $(list).attr('targetList3');
            var listCol4 = $(list).attr('targetList4');
            if (listCol2)
            {
                setAttr(listCol2,'graph_uri',graph_uri);
                // clean previously selected entity type
                targetTxt = $('#'+listCol2).attr('targetTxt');

                setAttr(targetTxt,'uri','');
                $('#'+targetTxt).html('Select a Property + <span style="color:blue"><strong> example value </strong></span>');
                setAttr(targetTxt,'style','background-color:none');

                // get the distinct predicates and example values of a graph into a list group
                $('#'+listCol2).html('Loading...');
            }
            if (listCol3)
            {
                setAttr(listCol3,'graph_uri',graph_uri);
                // clean previously selected entity type
                targetTxt = $('#'+listCol3).attr('targetTxt');

                setAttr(targetTxt,'uri','');
                $('#'+targetTxt).html('Select a Property + <span style="color:blue"><strong> example value </strong></span>');
                setAttr(targetTxt,'style','background-color:none');

                // get the distinct predicates and example values of a graph into a list group
                $('#'+listCol3).html('Loading...');
            }
            if (listCol4)
            {
                setAttr(listCol4,'graph_uri',graph_uri);
                // clean previously selected entity type
                targetTxt = $('#'+listCol4).attr('targetTxt');

                setAttr(targetTxt,'uri','');
                $('#'+targetTxt).html('Select a Property + <span style="color:blue"><strong> example value </strong></span>');
                setAttr(targetTxt,'style','background-color:none');

                // get the distinct predicates and example values of a graph into a list group
                $('#'+listCol4).html('Loading...');
            }

            var total = $(th).attr('total');
            if (!total)
                total = ''
            var type = $(th).attr('uri');
            if (graph_uri == '')
            {
                graph_uri = $(th).attr('uri');
                type = ''
            }

            $.get('/getpredicates', data={'dataset_uri': graph_uri, 'type': type, 'total': total,
                                          'function': 'selectionClick(this, "pred-list");'},
                                    function(data)
            {  // load the rendered template into the column target list col
                var obj = JSON.parse(data);
                if (obj.message == 'OK')
                {
                    $('#'+listCol).html(obj.result);
                    if ($('#'+listCol).attr('badge_counter')) {
                       var badge_counter = $('#'+listCol).attr('badge_counter');
                       var ul = document.getElementById(listCol);
                       var li = ul.getElementsByTagName('li');
                       var num = ('0000' + String(li.length)).substr(-4);
                       $('#'+badge_counter).html(num);
                    }
                    if (listCol2) {
                        $('#'+listCol2).html(obj.result);
                        if ($('#'+listCol2).attr('badge_counter')) {
                           var badge_counter = $('#'+listCol2).attr('badge_counter');
                           var ul = document.getElementById(listCol2);
                           var li = ul.getElementsByTagName('li');
                           var num = ('0000' + String(li.length)).substr(-4);
                           $('#'+badge_counter).html(num);
                        }
                    }
                    if (listCol3) {
                        $('#'+listCol3).html(obj.result);
                        if ($('#'+listCol3).attr('badge_counter')) {
                           var badge_counter = $('#'+listCol3).attr('badge_counter');
                           var ul = document.getElementById(listCol3);
                           var li = ul.getElementsByTagName('li');
                           var num = ('0000' + String(li.length)).substr(-4);
                           $('#'+badge_counter).html(num);
                        }
                    }
                    if (listCol4) {
                        $('#'+listCol4).html(obj.result);
                        if ($('#'+listCol4).attr('badge_counter')) {
                           var badge_counter = $('#'+listCol4).attr('badge_counter');
                           var ul = document.getElementById(listCol4);
                           var li = ul.getElementsByTagName('li');
                           var num = ('0000' + String(li.length)).substr(-4);
                           $('#'+badge_counter).html(num);
                        }
                    }
                }
                else
                    $('#'+listCol).html(obj.message);
            });
        }
        else if ((checkPropPath.checked) && ($('#'+listCol).attr('propPath')!='disabled'))
        {
            // check if the value of the selected property is of type uri
            if ($(th).attr('obj_type') == 'uri')
            {    // if the user choose to use property path
                // then the pred-list will be reloaeded with the predicates
                // that are available for the objects of the selected property
                // if (property_path is selected)
                var preivousContentListCol = $('#'+listCol).html();
                $('#'+listCol).html('Loading...');
                $.get('/getpredicates', data={'dataset_uri': graph_uri, 'propPath': propPath,
                                          'function': 'selectionClick(this, "pred-list");'},
                                    function(data)
                {  // load the rendered template into the column target list col
                    var obj = JSON.parse(data);
                    if (obj.message == 'OK')
                    {    $('#'+listCol).html(obj.result);
                        if ($('#'+listCol).attr('badge_counter')) {
                           var badge_counter = $('#'+listCol).attr('badge_counter');
                           var ul = document.getElementById(listCol);
                           var li = ul.getElementsByTagName('li');
                           var num = ('0000' + String(li.length)).substr(-4);
                           $('#'+badge_counter).html(num);
                        }
                    }
                    else
                    { if (obj.message == 'Empty')
                        {    // it is a uri but not a valid property path
                            // restore the preivous content
                            $('#'+listCol).html(preivousContentListCol);
                            // disable the continuation of property path
                            setAttr(listCol,'propPath','disabled');
                        }
                        else
                        {    $('#'+listCol).html(obj.message); }
                    }
                });
            }
            else
            {
                setAttr(listCol,'propPath','disabled');
            }
        }
    }
}



function resetDivSelectedEntity(button_id,mode)
{
    if (mode == 'predicate')
    {
//        alert('test');
        var button = document.getElementById(button_id) //button-src-entity-type-col
        var predList = $(button).attr('targetList');

        // clear the selection of predicates
        setAttr(predList,'propPath','enabled');
        var selectedPredDiv = $('#'+predList).attr('targetTxt');
        setAttr(selectedPredDiv,'uri','');
        $('#'+selectedPredDiv).html('Select a Property + <span style="color:blue"><strong> example value </strong></span>');
        setAttr(selectedPredDiv,'style','background-color:none');

        // reload the predicates list
        var hidden_divs = button.getElementsByClassName('hiddenDiv');
        var target = $(button).attr('targetTxt');
        var hiddenDiv = $(button).attr('hiddenDiv');
        if (hiddenDiv)
        {
//                alert(hiddenDiv);
                $(button).html($(button).html() + '<div class="hiddenDiv" id="' + hiddenDiv +'" style="display:none" uri="" label="" ></div>')
                setAttr(hiddenDiv,'uri',$('#'+target).attr('uri'));
                setAttr(hiddenDiv,'label',$('#'+target).html());
                var elem = document.getElementById(hiddenDiv);
                // TODO Fix error finding the ancestor of hiddenDiv
                selectionClick(elem, "entity-list");
        }
    }
}

function resetDivEnrichmentDts(button_id,targetList)
{
        var button = document.getElementById(button_id) //button-src-entity-type-col
        var predList = $(button).attr(targetList);

        setAttr(predList,'propPath','enabled');
        var selectedPredDiv = $('#'+predList).attr('targetTxt');
        setAttr(selectedPredDiv,'uri','');
        $('#'+selectedPredDiv).html('Select a Property + <span style="color:blue"><strong> example value </strong></span>');
        setAttr(selectedPredDiv,'style','background-color:none');

        // reload the predicates list
        $('#'+predList).html($('#dataset_predicates_col').html());

}


// Function fired onclick of a methods from list
function methodClick(th)
{
    var description = '';
    var method = $(th).attr('uri');
    var meth_label = $(th).attr('label');
    $('#int_red_graph_row').hide();
    $('#aprox_settings_row').hide();
    $('#aprox_nbr_settings_row').hide();

    if (method == 'identity')
    {
      //refresh_create_linkset(mode='pred');
      $('#src_selected_pred_row').hide();
      $('#src_list_pred_row').hide();
      $('#trg_selected_pred_row').hide();
      $('#trg_list_pred_row').hide();
      description = `The method <b>IDENTITY</b> aligns the <b>identifier of the source</b> with the <b>identifier of the target</b>.
                     This implies that both datasets use the same Unified Resource Identifier (URI).`;
    }
    else if (method == 'embededAlignment')
    {
      //refresh_create_linkset(mode='pred');
      $('#src_selected_pred_row').show();
      $('#src_list_pred_row').show();
      $('#trg_selected_pred_row').hide();
      $('#trg_list_pred_row').hide();
      description = `The method <b>EMBEDED ALIGNMENT EXTRATION</b> extracts an alignment already provided within the <b>source</b> dataset.
                     The extraction relies on the value of the linking <b>property</b>, i.e. <b>property of the source</b> that holds the <b>identifier of the target</b>. However, the real mechanism used to create the alignment is not explicitly provided by the source.`;
    }
    else if (method == 'loadLinkset')
    {
      //refresh_create_linkset(mode='pred');
      $('#src_selected_pred_row').show();
      $('#src_list_pred_row').show();
      $('#trg_selected_pred_row').hide();
      $('#trg_list_pred_row').hide();
      $('#dropbox_linkset_row').show();
      description = `The method `+ '"' +`<b>LOADS EXISTING LINKSET</b>`+ '"' +` load the alignment provided within an RDF
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
          description = 'The method <b>EXACT STRING-based SIMILARITY</b> is used to align the <b>source</b> and the <b>target</b> by matching the (string) values of the selected <b>properties<b>.';
        }
        else if (method == 'approxStrSim')
        {
          description = 'The method <b>APPROXIMATE STRING-based SIMILARITY</b> is used to align the <b>source</b> and the <b>target</b> by approximating the match of the (string) values of the selected <b>properties</b> according to a threshold. </br> Optionally, an existing alignment can be provided as a <b>reducer</b>, i.e. the resources already aligned will not be included in the new alignment. It allows for more efficient use of approximate similarity.';
          $('#selected_int_red_graph').html("Select an alingment as reducer");
          setAttr( 'selected_int_red_graph','style','background-color:none;');
          $('#int_red_graph_row').show();
          $('#aprox_settings_row').show();
          $('#button_int_red_graph').html('Loading...');
          rq_elem = document.getElementById('creation_idea_selected_RQ');
          rq_uri = $(rq_elem).attr('uri');
          if (rq_uri!='')
          {
              $.get('/getgraphsperrqtype',
                      data={'rq_uri': rq_uri,
                            'template': 'list_dropdown.html',
                            'btn_name': 'Alignment',
                            'type': 'linkset&lens',
                            'function': 'intRedGraphClick(this);'},
                      function(data)
              {
                    $('#button_int_red_graph').html(data);
              });
          }
        }
        else if (method == 'approxNbrSim')
        {
          description = 'The method <b>APPROXIMATE NUMBER-based SIMILARITY</b> is used to align the <b>source</b> and the <b>target</b> by approximating the match of the (number/date) values of the selected <b>properties</b> according to a delta. </br> Optionally, an existing alignment can be provided as a <b>reducer</b>, i.e. the resources already aligned will not be included in the new alignment. It allows for more efficient use of approximate similarity.';
          $('#aprox_nbr_settings_row').show();
//          $('#selected_int_red_graph').html("Select an alingment as reducer");
//          setAttr( 'selected_int_red_graph','style','background-color:none;');
//          $('#int_red_graph_row').show();
//          $('#aprox_settings_row').show();
//          $('#button_int_red_graph').html('Loading...');
        }
        else if (method == 'geoSim')
        {
          description = 'The method <b>GEO SIMILARITY</b> is used to align the <b>source</b> and the <b>target</b> by detecting whether the values of the selected <b>properties</b> of source and target appear within the same geographical boundary.';
        }
        else if (method == 'intermediate')
        {
          description = 'The method <b>MATCH VIA INTERMEDIATE DATASET</b> is used to align the <b>source</b> and the <b>target</b> by using <b>properties</b> that present different descriptions of a same entity, such as country name and country code. This is possible by providing an <b>intermediate dataset</b> that binds the two alternative descriptions to the very same identifier.';
          $('#int_red_graph_row').show();
          $('#button_int_red_graph').html('Loading...');
          $.get('/getdatasets',
                  data={'template': 'list_dropdown.html',
                        'function': 'datasetClick(this);'},
                  function(data)
          {
                $('#button_int_red_graph').html(data);
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



// Function fired onclick of a methods from list
function methodClickLens(th)
{
    var description = '';
    var method = $(th).attr('uri');
    var meth_label = $(th).attr('label');
    $('#refine_lens_int_red_graph_row').hide();
    $('#refine_lens_aprox_settings_row').hide();
    $('#refine_lens_aprox_nbr_settings_row').hide();

    if (method == 'identity')
    {
      //refresh_create_linkset(mode='pred');
      $('#refine_lens_src_selected_pred_row').hide();
      $('#refine_lens_src_list_pred_row').hide();
      $('#refine_lens_trg_selected_pred_row').hide();
      $('#refine_lens_trg_list_pred_row').hide();
      description = `The method <b>IDENTITY</b> aligns the <b>identifier of the source</b> with the <b>identifier of the target</b>.
                     This implies that both datasets use the same Unified Resource Identifier (URI).`;
    }
    else if (method == 'embededAlignment')
    {
      //refresh_create_linkset(mode='pred');
      $('#refine_lens_src_selected_pred_row').show();
      $('#refine_lens_src_list_pred_row').show();
      $('#refine_lens_trg_selected_pred_row').hide();
      $('#refine_lens_trg_list_pred_row').hide();
      description = `The method <b>EMBEDED ALIGNMENT EXTRATION</b> extracts an alignment already provided within the <b>source</b> dataset.
                     The extraction relies on the value of the linking <b>property</b>, i.e. <b>property of the source</b> that holds the <b>identifier of the target</b>. However, the real mechanism used to create the alignment is not explicitly provided by the source.`;
    }
    else if (method == 'loadLinkset')
    {
      //refresh_create_linkset(mode='pred');
      $('#refine_lens_src_selected_pred_row').show();
      $('#refine_lens_src_list_pred_row').show();
      $('#refine_lens_trg_selected_pred_row').hide();
      $('#refine_lens_trg_list_pred_row').hide();
      $('#refine_lens_dropbox_linkset_row').show();
      description = `The method `+ '"' +`<b>LOADS EXISTING LINKSET</b>`+ '"' +` load the alignment provided within an RDF
                    file and convert it according to the Lenticular Lens model. Source and target datasets,
                    as well as Entity Type are mandatory. Other metadata can be filled in for documentation purpose.`;

    }
    else
    {
        //refresh_create_linkset(mode='pred');
        $('#refine_lens_src_selected_pred_row').show();
        $('#refine_lens_src_list_pred_row').show();
        $('#refine_lens_trg_selected_pred_row').show();
        $('#refine_lens_trg_list_pred_row').show();
        if (method == 'exactStrSim')
        {
          description = 'The method <b>EXACT STRING-based SIMILARITY</b> is used to align the <b>source</b> and the <b>target</b> by matching the (string) values of the selected <b>properties<b>.';
        }
        else if (method == 'approxStrSim')
        {
          description = 'The method <b>APPROXIMATE STRING-based SIMILARITY</b> is used to align the <b>source</b> and the <b>target</b> by approximating the match of the (string) values of the selected <b>properties</b> according to a threshold. </br> Optionally, an existing alignment can be provided as a <b>reducer</b>, i.e. the resources already aligned will not be included in the new alignment. It allows for more efficient use of approximate similarity.';
          $('#refine_lens_selected_int_red_graph').html("Select an alingment as reducer");
          setAttr( 'refine_lens_selected_int_red_graph','style','background-color:none;');
          $('#refine_lens_int_red_graph_row').show();
          $('#refine_lens_aprox_settings_row').show();
          $('#refine_lens_button_int_red_graph').html('Loading...');
          rq_elem = document.getElementById('creation_idea_selected_RQ');
          rq_uri = $(rq_elem).attr('uri');
          if (rq_uri!='')
          {
              $.get('/getgraphsperrqtype',
                      data={'rq_uri': rq_uri,
                            'template': 'list_dropdown.html',
                            'btn_name': 'Alignment',
                            'type': 'linkset&lens',
                            'function': 'intRedGraphClick(this);'},
                      function(data)
              {
                    $('#refine_lens_button_int_red_graph').html(data);
              });
          }
        }
        else if (method == 'approxNbrSim')
        {
          description = 'The method <b>APPROXIMATE NUMBER-based SIMILARITY</b> is used to align the <b>source</b> and the <b>target</b> by approximating the match of the (number/date) values of the selected <b>properties</b> according to a delta. </br> Optionally, an existing alignment can be provided as a <b>reducer</b>, i.e. the resources already aligned will not be included in the new alignment. It allows for more efficient use of approximate similarity.';
          $('#refine_lens_aprox_nbr_settings_row').show();
//          $('#selected_int_red_graph').html("Select an alingment as reducer");
//          setAttr( 'selected_int_red_graph','style','background-color:none;');
//          $('#int_red_graph_row').show();
//          $('#aprox_settings_row').show();
//          $('#button_int_red_graph').html('Loading...');
        }
        else if (method == 'geoSim')
        {
          description = 'The method <b>GEO SIMILARITY</b> is used to align the <b>source</b> and the <b>target</b> by detecting whether the values of the selected <b>properties</b> of source and target appear within the same geographical boundary.';
        }
        else if (method == 'intermediate')
        {
          description = 'The method <b>MATCH VIA INTERMEDIATE DATASET</b> is used to align the <b>source</b> and the <b>target</b> by using <b>properties</b> that present different descriptions of a same entity, such as country name and country code. This is possible by providing an <b>intermediate dataset</b> that binds the two alternative descriptions to the very same identifier.';
          $('#refine_lens_int_red_graph_row').show();
          $('#refine_lens_button_int_red_graph').html('Loading...');
          $.get('/getdatasets',
                  data={'template': 'list_dropdown.html',
                        'function': 'datasetClick(this);'},
                  function(data)
          {
                $('#refine_lens_button_int_red_graph').html(data);
          });

        }
    }

    // Attribute the label of the selected method to the div
    // where the name is displayed
    setAttr('refine_lens_selected_meth','uri',method);
    //setAttr('selected_meth','label',meth_label);
    $('#refine_lens_selected_meth').html(meth_label);
    setAttr('refine_lens_selected_meth','style','background-color:lightblue');
    $('#refine_lens_selected_method_desc').html(description);
}

///////////////////////////////////////////////////////////////////////////////
// Functions for refreshing selection elements in each div
///////////////////////////////////////////////////////////////////////////////
function refresh_create_linkset(mode='all')
{
    chronoReset();
    var elem = Object;
    $('#linkset_creation_message_col').html("");
    $('#linkset_import_message_col').html("");
    $('#linkset_edit_message_col').html("");

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
      $('#creation_linkset_search_row').hide();
      $('#creation_linkset_correspondence_row').hide();
      $('#creation_linkset_correspondence_col').html('');

      $('#int_red_graph_row').hide();
      $('#aprox_settings_row').hide();
      elem = document.getElementById('selected_int_red_graph');
      elem.setAttribute('uri', '');
      elem.setAttribute('style', 'background-color:none');
      $('#selected_int_red_graph').html("Select a Dataset");

      $('#linkset_refine_message_col').html('');

      $('#button-src-col').html('<div id="hidden_src_div" style="display:none" uri="" label="" ></div>');
      $('#button-trg-col').html('<div id="hidden_trg_div" style="display:none" uri="" label="" ></div>');
    }

    if (mode == 'all' || mode == 'source')
    {

      elem = document.getElementById('button-src-entity-type-col');
//      console.log(elem);
      var content = '<div id="hidden_src_entType_div" style="display:none" uri="" label="" ></div>';
      content += '<button class="btn btn-primary btn-round dropdown-toggle" type="button"';
      content += 'data-toggle="dropdown">Entity Type<span class="caret"></span></button>';
//      alert(content);
      $(elem).html(content);
//      console.log(elem);

      elem = document.getElementById('src_selected_entity-type');
      $(elem).html("Select an Entity Type");
      elem.setAttribute('uri', '');
      elem.setAttribute('style', 'background-color:none');

//      elem = document.getElementById('hidden_src_entType_div');
//      elem.setAttribute('uri', '');
//      elem.setAttribute('label', '');

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

      elem = document.getElementById('button-trg-entity-type-col');
      var content = '<div id="hidden_trg_entType_div" style="display:none" uri="" label="" ></div>';
      content += '<button class="btn btn-primary btn-round dropdown-toggle" type="button"';
      content += 'data-toggle="dropdown">Entity Type<span class="caret"></span></button>';
      $(elem).html(content);

      elem = document.getElementById('trg_selected_entity-type');
      $(elem).html("Select an Entity Type");
      elem.setAttribute('uri', '');
      elem.setAttribute('style', 'background-color:none');

//      elem = document.getElementById('hidden_trg_entType_div');
//      elem.setAttribute('uri', '');
//      elem.setAttribute('label', '');

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
    $('#lens_edit_message_col').html("");
    $('#lens_add_filter_message_col').html("");
    $('#lens_add_filter_message_col').html("");
    $('#selected_operator').html("Select a Operator");
    $('#selected_operator_desc').html("Operator Description");
//    $('#creation_linkset_correspondence_row').hide();
//    $('#creation_linkset_correspondence_col').html('');
    $('#creation_lens_correspondence_row').hide();
    $('#creation_lens_correspondence_col').html('');
    $('#inspect_lens_lens_details_col').html('');
    chronoReset();
}


function refresh_create_idea()
{
    $('#creation_idea_registered_graphtype_list').html("");
    $('#creation_idea_graphtype_list').html("");
}


function refresh_create_view(mode='all')
{
//    alert('here');
    if (mode == 'all')
    {   var btn = document.getElementById('detailsViewButton');
        resetButton(btn);
        btn = document.getElementById('createViewButton');
        resetButton(btn);
        $('#view_creation_message_col').html("");
        $('#view_creation_save_message_col').html("");
        $('#inspect_views_details_col').html("");
        $('#creation_view_linkset_col').html("");
        $('#creation_view_lens_col').html("");
        $('#creation_view_selected_predicates_group').html("");
    }
//    if (mode=='query')
//    {
        $('#views-results').html("");
        $('#queryView').val("");
//    }
    chronoReset();
}


function refresh_import(mode='all')
{
    if (mode == 'all')
    { $('#dropbox').html('<span class="message"><strong><font size="6">Drop here your files to upload.</font></strong></span>');
    }

    $('#ds_files_list').html(select_file);
    $('#upload_sample').val('NO DATASET FILE SELECTED');

    $('#dataset_header').val('NO DATASET FILE SELECTED');
    $('#ds_separator').val('');
    $('#ds_name').val('');
    $('#ds_entity_type_name').val('');
    $('#ds_subject_id').html('');
    $('#ds_type_list').html('');

    $('#schema_sample').val('NO DATASET FILE SELECTED');
    $('#dataset_sample').val('NO DATASET FILE SELECTED');

    $('#dataset_upload_message_col').html('');
    $('#dataset_convertion_message_col').html('');
    $('#dataset_schema_message_col').html('');
    $('#converted_sample_message_col').html('');

    $('#dataset_load').val('NO DATASET FILE SELECTED');
    $('#import_alignment').val('NO DATASET FILE SELECTED');

    $('#dataset_creation_message_col').html('');
    $('#import_alignment_message_col').html('');

    chronoReset();
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
    $('#import_title').html('<h3>Import Dataset</h3>');
    $('#dataset_upload_row').show();
    $('#dataset_convert_row').show();
    $('#import_dataset_div').show();
    $('#viewDatasetButton').show();
    $('#import_alignment_div').hide();
    $('#viewAlignmentButton').hide();
    refresh_import();
}


function import_alignent_button(th)
{
    $('#import_title').html('<h3>Import Alignment</h3>');
    $('#dataset_upload_row').show();
    $('#dataset_convert_row').show();
    $('#import_alignment_div').show();
    $('#viewAlignmentButton').show();
    $('#import_dataset_div').hide();
    $('#viewDatasetButton').hide();
    refresh_import();
}


$(".panel-collapse").on('hidden.bs.collapse', function(){
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


$(".panel-collapse").on('shown.bs.collapse', function(){
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

    console.log(files);
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

        loadingGif(document.getElementById('dataset_convertion_message_col'), 2);

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

            loadingGif(document.getElementById('dataset_convertion_message_col'), 2, show=false);

            var obj = data
//            console.log(obj);
            if (Object.keys(obj).length)
            {
                //$('#button_int_red_graph').html(data);
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

    if ((files.length > 0) && (files[0] != '-- Select a file to view a sample --'))
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


function viewSampleAlignFileClick()
{
    var file = $('#viewAlignmentButton').attr('file_path');

    if (file)
    {
        $.get('/viewSampleFile',
              data={'file':  file, 'size':1000},
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
        $.post('/headerExtractor',
          data={'header_line': input.value, 'separator': separator.value},
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

        loadingGif(document.getElementById('dataset_creation_message_col'), 2);
        $('#dataset_creation_message_col').html(addNote(loading_dataset,cl='warning'));
        $.get('/loadGraph',
              data={'batch_file': $('#createDatasetButton').attr('batchFile')},
              function(data)
            {
                loadingGif(document.getElementById('dataset_creation_message_col'), 2, show=false);
                  var obj = JSON.parse(data);
//                  console.log(obj);
                  $('#dataset_load').val(obj);
                  $('#dataset_creation_message_col').html(addNote(loaded_dataset,cl='success'));

            });
    }
    else
    {
        $('#dataset_creation_message_col').html(addNote(missing_feature));
    }
}


$('#ds_files_list').change(function() {

    if (selectedButton(document.getElementById('btn_import_alignment')))
    {
        var selectedText = $(this).find("option:selected").text();
        if (selectedText != "-- Select a predicate --")
        {   enableButton('importAlignmentButton')
        }
        else
        {   enableButton('importAlignmentButton', enable=false)
        }
    }
});


function importAlignmentClick()
{
    var file_path = $('#viewAlignmentButton').attr('file_path');
    var indexes_1 = []
    indexes_1 = getSelectIndexes(document.getElementById('ds_files_list'));
    if (indexes_1.length != 0)
    {
        var index = indexes_1[0];
        if ((file_path) && (index))
        {
            $('#import_alignment_message_col').html(addNote(loading_dataset,cl='warning'));
            $.get('/userLinksetImport',
              data={'original': file_path,
                    'index': index},
              function(data)
            {
                  var obj = JSON.parse(data);
//                  console.log(obj);
                  $('#import_alignment').val(obj);
                  $('#import_alignment_message_col').html(addNote(loaded_dataset,cl='success'));
            });
        }
    }
//        {
//            var rdftype = indexes_1;
//        }
//        else
//        {
//            var rdftype = [];
//        }
}


$('.btn-toggle').click(function() {
    $(this).find('.btn').toggleClass('active');

    if ($(this).find('.btn-primary').size()>0) {
    	$(this).find('.btn').toggleClass('btn-primary');
    }
    if ($(this).find('.btn-danger').size()>0) {
    	$(this).find('.btn').toggleClass('btn-danger');
    }
    if ($(this).find('.btn-success').size()>0) {
    	$(this).find('.btn').toggleClass('btn-success');
    }
    if ($(this).find('.btn-info').size()>0) {
    	$(this).find('.btn').toggleClass('btn-info');
    }

    $(this).find('.btn').toggleClass('btn-default');

});


////////////////////////////////////////////////////////
//Dataset Inspection
////////////////////////////////////////////////////////

function dataset_stats_load_datasets_predicates()
{
// Load into div the selected datasets for a certain research question
    var rq_uri = $('#dataset_inspection_selected_RQ').attr('uri');
     $('#dataset_linking_stats_selection_prop_dataset_col').html('Loading...');
     $.get('/getgraphsentitytypes',data={'rq_uri': rq_uri, 'mode': 'view'},function(data)
     {
       $('#dataset_linking_stats_selection_prop_dataset_col').html(data);

       // when a dataset from the list is selected, its list of predicates will be loaded
       $('#dataset_linking_stats_selection_prop_dataset_col li').on('click',function()
       {
          var graph_uri = $(this).attr('uri');
          var graph_label = $(this).attr('label');
          var type_uri = $(this).attr('type_uri');
          var type_label = $(this).attr('type_label');
          var total = $(this).attr('total');

          if (selectListItemUnique(this, 'dataset_linking_stats_selection_prop_dataset_col'))
          {
              // Exhibit a waiting message for the user to know loading time might be long.
              $('#dataset_linking_stats_selection_prop_predicates_col').html('Loading...');
              // get the distinct predicates and example values of a graph into a list group
              $.get('/getpredicates',data={'dataset_uri': graph_uri, 'type': type_uri, 'total': total},function(data)
              {
                  // load the rendered template into the column #creation_view_predicates_col
                  var obj = JSON.parse(data);
                  if (obj.message == 'OK') {
                       $('#dataset_linking_stats_selection_prop_predicates_col').html(obj.result);
                       var ul = document.getElementById('dataset_linking_stats_selection_prop_predicates_col');
                       var li = ul.getElementsByTagName('li');
                       var num = ('0000' + String(li.length)).substr(-4);
                       $('#dataset_linking_stats_selection_prop_pred_counter').html(num);
                  }
                  else
                        $('#dataset_linking_stats_selection_prop_predicates_col').html(obj.message);

                  // set actions after clicking one of the predicates
                  $('#dataset_linking_stats_selection_prop_predicates_col li').on('click',function()
                  {
                    var pred_uri = $(this).attr('uri');
                    var pred_label = $(this).attr('label');

                    var i;
                    var check = false;
                    var elem = document.getElementById('dataset_linking_stats_selection_prop_selected_predicates_group');
                    if (elem) {
                        var elems = elem.getElementsByClassName('list-group-item');
                        for (i = 0; i < elems.length; i++) {
                            if ( ($(elems[i]).attr('pred_uri') == pred_uri)
                                     && ($(elems[i]).attr('graph_uri') == graph_uri) )
                            {
                              check = true;
                              break;
                            }
                        }
                        if (!check) {
                           var item = '<li class="list-group-item" pred_uri="' + pred_uri
                                    + '" graph_uri="' + graph_uri
                                    + '" type_uri="' + type_uri
                                    + '" onclick= "this.parentElement.removeChild(this);"'
                                    + '><span class="list-group-item-heading"><b>'
                                    + graph_label + ' | ' + type_label + '</b>: ' + pred_label + '</span></li>';
                           $('#dataset_linking_stats_selection_prop_selected_predicates_group').prepend(item);
                        }
                    }
                  });
              });
          }

       });
     });

//     if ((view_filters) && (view_filters.length > 0))
//     {
//        $('#dataset_linking_stats_selection_prop_selected_predicates_group').html("");
//        //var view_filters = obj.list_pred
//        for (i = 0; i < view_filters.length; i++) {
//              $('#dataset_linking_stats_selection_prop_selected_predicates_group').prepend(view_filters[i]);
//        }
//     }
}


function dataset_stats_load_linksets_lenses()
{
    var rq_uri = $('#dataset_inspection_selected_RQ').attr('uri');
  $('#dataset_linking_stats_selection_linkset_col').html('Loading...');
     $.get('/getgraphsperrqtype',data={'rq_uri': rq_uri,
                            'type': 'linkset',
                            'template': 'list_group.html',
                            'dataset': $('#selected_dataset').attr('uri')},function(data)
     {
       $('#dataset_linking_stats_selection_linkset_col').html(data);
       var ul = document.getElementById('dataset_linking_stats_selection_linkset_col');
       var a = ul.getElementsByTagName('a');
       var num = ('0000' + String(a.length)).substr(-4);
       $('#dataset_linking_stats_selection_linkset_counter').html(num);

       // set actions after clicking a graph in the list
       $('#dataset_linking_stats_selection_linkset_col a').on('click',function()
       {
          var uri = $(this).attr('uri');
          selectListItem(this);
       });
      });

     $('#dataset_linking_stats_selection_lens_col').html('Loading...');
     $.get('/getgraphsperrqtype',data={'rq_uri': rq_uri,
                            'type': 'lens',
                            'template': 'list_group.html'},function(data)
     {
       $('#dataset_linking_stats_selection_lens_col').html(data);
       var ul = document.getElementById('dataset_linking_stats_selection_lens_col');
       var a = ul.getElementsByTagName('a');
       var num = ('0000' + String(a.length)).substr(-4);
       $('#dataset_linking_stats_selection_lens_counter').html(num);

       // set actions after clicking a graph in the list
       $('#dataset_linking_stats_selection_lens_col a').on('click',function()
       {
          var uri = $(this).attr('uri');
          selectListItem(this);
        });
     });

}

$('#selectAllLinksetsCheckBok').click(function() {
    if (this.checked)
    {
        selectAllListItems('dataset_linking_stats_selection_linkset_col')
   }
   else
   {  deselectAllListItems('dataset_linking_stats_selection_linkset_col');
   }
});


$('#selectAllLensesCheckBok').click(function() {
    if (this.checked)
    {
        selectAllListItems('dataset_linking_stats_selection_lens_col')
   }
   else
   {  deselectAllListItems('dataset_linking_stats_selection_lens_col');
   }
});

function calculateFreqClick(){
    var btn = document.getElementById('btn_freq_type');
    var elems = btn.getElementsByClassName('active');

    if (elems.length > 0) {
        $.get('/calculateFreq',
              data={'dataset': $('#selected_dataset').attr('uri'),
                    'entityType': $('#dts_selected_entity-type').attr('uri'),
                    'property': $('#dataset_stat_selected_pred').attr('uri'),
                    'freqType': $(elems[0]).attr('type') },
              function(data)
            {
                  $('#dataset_stats_values_col').html(data);
                   var ul = document.getElementById('dataset_stats_values_col');
                   var li = ul.getElementsByTagName('li');
                   var num = ('0000' + String(li.length)).substr(-4);
                   $('#dataset_stat_values_counter').html(num);
    //                  $('#dataset_creation_message_col').html(addNote(loaded_dataset,cl='success'));
            });
    }
}


function calculateDatasetStats()
{
    $('#dataset_linking_stats_message_col').html(addNote('The query is running.',cl='warning'));
    loadingGif(document.getElementById('dataset_linking_stats_message_col'), 2);

    d3.selectAll("svg > *").remove();
    $('#chart_dataset_linking_stats').html('');
    $('#dataset_linking_stats_results').html('');
    $("#collapse_dataset_linking_stats_graphic").collapse("hide");


    var checkOptionalLabel = document.getElementById('optionalLabelCheckBok');
    if (checkOptionalLabel.checked)
        var optionalLabel = 'no';
    else
        var optionalLabel = 'yes';

    var checkComputerCluster = document.getElementById('computeClusterCheckBok');
    if (checkComputerCluster.checked)
        var computeCluster = 'yes';
    else
        var computeCluster = 'no';

    var elems = selectedElemsInGroupList('dataset_linking_stats_selection_linkset_col');
    var i;
    var alignments = []
    for (i = 0; i < elems.length; i++) {
        alignments.push($(elems[i]).attr('uri'));
    }
    elems = selectedElemsInGroupList('dataset_linking_stats_selection_lens_col');
    for (i = 0; i < elems.length; i++) {
        alignments.push($(elems[i]).attr('uri'));
    }

    if (alignments.length > 0)
    {
      $.get('/getDatasetLinkingStats',data={'dataset': $('#selected_dataset').attr('uri'),
                                     'entityType': $('#dts_selected_entity-type').attr('uri'),
                                     'optionalLabel': optionalLabel,
                                     'computeCluster': computeCluster,
                                     'alignments[]': alignments}, function(data)
      {
        var obj = JSON.parse(data);
        $('#dataset_linking_stats_results').html(obj.result);
        $("#collapse_dataset_linking_stats_table").collapse("show");
        $('#dataset_linking_stats_message_col').html(addNote(obj.message,cl='info'));

        if (checkComputerCluster.checked)
            plotDatasetLinkingStats4(obj.plotdata);
        else
            plotDatasetLinkingStats3(obj.plotdata);
        $("#collapse_dataset_linking_stats_graphic").collapse("show");

        loadingGif(document.getElementById('dataset_linking_stats_message_col'), 2, show = false);

      });
    }
    else
    {
        $('#dataset_linking_stats_message_col').html(addNote(missing_feature));
    }
}

function calculateDatasetCluster()
{

    $('#dataset_linking_stats_cluster_results').html('');
    $('#dataset_linking_stats_cluster_results_details').html('');
    $("#collapse_dataset_linking_stats_cluster").collapse("hide");
    $("#collapse_dataset_linking_stats_cluster_details").collapse("hide");

    var properties = []
    var elem = document.getElementById('dataset_linking_stats_selection_prop_selected_predicates_group');
    if (elem) { elems = elem.getElementsByClassName('list-group-item'); }
    for (i = 0; i < elems.length; i++) {
        properties.push( $(elems[i]).attr('pred_uri').replace('>',"").replace('<',"") );
    }

    var elems = selectedElemsInGroupList('dataset_linking_stats_selection_linkset_col');
    var i;
    var alignments = []
    for (i = 0; i < elems.length; i++) {
        alignments.push($(elems[i]).attr('uri'));
    }
    elems = selectedElemsInGroupList('dataset_linking_stats_selection_lens_col');
    for (i = 0; i < elems.length; i++) {
        alignments.push($(elems[i]).attr('uri'));
    }

    if ((alignments.length > 0) && (properties.length > 0))
    {
        $('#dataset_linking_cluster_message_col').html(addNote('The query is running.',cl='warning'));
        loadingGif(document.getElementById('dataset_linking_cluster_message_col'), 2);

      $.get('/getDatasetLinkingClusters',data={'dataset': $('#selected_dataset').attr('uri'),
                                     'entityType': $('#dts_selected_entity-type').attr('uri'),
                                     'alignments[]': alignments,
                                     'properties[]': properties}, function(data)
      {
        var obj = JSON.parse(data);
        $('#dataset_linking_stats_cluster_results').html(obj.result);
        $("#collapse_dataset_linking_stats_cluster").collapse("show");
        $('#dataset_linking_cluster_message_col').html(addNote(obj.message,cl='info'));
        loadingGif(document.getElementById('dataset_linking_cluster_message_col'), 2, show = false);

       // set actions after clicking a graph in the list
       $('#dataset_linking_stats_cluster_results TR').on('click',function(e){
            var checkboxGroupDistValues = document.getElementById('checkboxGroupDistValues');
            if (checkboxGroupDistValues.checked)
                var groupDistValues = 'yes';
            else
                var groupDistValues = 'no';
            $.get('/getDatasetLinkingClusterDetails',data={'cluster': $(this).attr('cluster'),
                                                           'groupDistValues': groupDistValues,
                                                           'properties[]': properties }, function(data)
            {
            var obj = JSON.parse(data);
            $('#dataset_linking_stats_cluster_results_details').html(obj.result);
            $("#collapse_dataset_linking_stats_cluster_details").collapse("show");

            });
        });
      });
    }
    else
    {
        $('#dataset_linking_cluster_message_col').html(addNote(missing_feature));
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



function plotDatasetLinkingStats3(data){
var margin = {top: 20, right: 30, bottom: 30, left: 40},
    width = 940 - margin.left - margin.right,
    height = 500 - margin.top - margin.bottom;

var x = d3.scale.ordinal()
    .rangeRoundBands([0, width], .1);

var y = d3.scale.linear()
    .range([height, 0]);

var xAxis = d3.svg.axis()
    .scale(x)
    .orient("bottom");

var yAxis = d3.svg.axis()
    .scale(y)
    .orient("left");
//    .ticks(10, "%");

var chart = d3.select(".chart")
    .attr("width", width + margin.left + margin.right)
    .attr("height", height + margin.top + margin.bottom)
  .append("g")
    .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

  x.domain(data.map(function(d) { return d.name; }));
  y.domain([0, d3.max(data, function(d) { return d.freq; })]);

  chart.append("g")
      .attr("class", "x axis")
      .attr("transform", "translate(0," + height + ")")
      .call(xAxis)
    .selectAll(".tick text")
      .call(wrap, x.rangeBand());

  chart.append("g")
      .attr("class", "y axis")
      .call(yAxis)
     .append("text")
        .attr("transform", "rotate(-90)")
        .attr("y", 6)
        .attr("dy", ".71em")
        .style("text-anchor", "end")
        .text("Frequency %");

  chart.selectAll(".bar")
      .data(data)
    .enter().append("rect")
      .attr("class", "bar")
      .attr("x", function(d) { return x(d.name); })
      .attr("y", function(d) { return y(d.freq); })
      .attr("height", function(d) { return height - y(d.freq); })
      .attr("width", x.rangeBand());

}


function plotDatasetLinkingStats4(data){

var margin = {top: 20, right: 30, bottom: 30, left: 40},
    width = 1040 - margin.left - margin.right,
    height = 500 - margin.top - margin.bottom;

var x = d3.scale.ordinal()
    .rangeRoundBands([0, width], .1);
var y0 = d3.scale.linear().range([height, 0]),
y1 = d3.scale.linear().range([height, 0]);

var xAxis = d3.svg.axis()
    .scale(x)
    .orient("bottom");
// create left yAxis
var yAxisLeft = d3.svg.axis().scale(y0).ticks(4).orient("left");
// create right yAxis
var yAxisRight = d3.svg.axis().scale(y1).ticks(6).orient("right");

var svg = d3.select(".chart")
    .attr("width", width + margin.left + margin.right)
    .attr("height", height + margin.top + margin.bottom)
  .append("g")
    .attr("class", "graph")
    .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

  x.domain(data.map(function(d) { return d.name; }));
  y0.domain([0, d3.max(data, function(d) { return Math.min(Math.max(1.5*d.freq, 1.5*d.clust), 100); })]);
  y1.domain([0, d3.max(data, function(d) { return Math.min(Math.max(1.5*d.freq, 1.5*d.clust), 100); })]);
//y1.domain([0, d3.max(data, function(d) { return Math.max(d.freq, d.clust); })]);

//  x.domain(data.map(function(d) { return d.year; }));
//  y0.domain([0, d3.max(data, function(d) { return d.money; })]);

  svg.append("g")
      .attr("class", "x axis")
      .attr("transform", "translate(0," + height + ")")
      .call(xAxis)
    .selectAll(".tick text")
      .call(wrap, x.rangeBand());

  svg.append("g")
	  .attr("class", "y axis axisLeft")
	  .attr("transform", "translate(0,0)")
	  .call(yAxisLeft)
	.append("text")
      .attr("transform", "rotate(-90)")
	  .attr("y", 6)
      .attr("dy", ".9em")
	  .attr("dx", "2em")
	  .style("text-anchor", "end")
	  .text("Frequency %");

  svg.append("g")
	  .attr("class", "y axis axisRight")
	  .attr("transform", "translate(" + (width) + ",0)")
	  .call(yAxisRight)
	.append("text")
      .attr("transform", "rotate(-90)")
	  .attr("y", 6)
	  .attr("dy", "-2em")
	  .attr("dx", "2em")
	  .style("text-anchor", "end")
	  .text("Clusters %");

  bars = svg.selectAll(".bar").data(data).enter();
  bars.append("rect")
      .attr("class", "bar1")
      .attr("x", function(d) { return x(d.name); })
      .attr("width", x.rangeBand()/2)
      .attr("y", function(d) { return y0(d.freq); })
	  .attr("height", function(d,i,j) { return height - y0(d.freq); })
	  .on("click",function(d){
	    alert(d.freq)
       });

  bars.append("rect")
      .attr("class", "bar2")
      .attr("x", function(d) { return x(d.name) + x.rangeBand()/2; })
      .attr("width", x.rangeBand() / 2)
      .attr("y", function(d) { return y1(d.clust); })
	  .attr("height", function(d,i,j) { return height - y1(d.clust); });

//  bars = svg.selectAll(".bar1").data(data)
//    .append("text")
//      .attr("x", x(d.name) / 2 )
//      .attr("y", function(d) { return y0(d.freq) + 3; })
//      .attr("dy", ".75em")
//      .text(function(d) { return d.freq; });

}


function wrap(text, width) {
  text.each(function() {
    var text = d3.select(this),
        words = text.text().split(/\s+/).reverse(),
        word,
        line = [],
        lineNumber = 0,
        lineHeight = 1.1, // ems
        y = text.attr("y"),
        dy = parseFloat(text.attr("dy")),
        tspan = text.text(null).append("tspan").attr("x", 0).attr("y", y).attr("dy", dy + "em");
    while (word = words.pop()) {
      line.push(word);
      tspan.text(line.join(" "));
      if (tspan.node().getComputedTextLength() > width) {
        line.pop();
        tspan.text(line.join(" "));
        line = [word];
        tspan = text.append("tspan").attr("x", 0).attr("y", y).attr("dy", ++lineNumber * lineHeight + dy + "em").text(word);
      }
    }
  });
}


