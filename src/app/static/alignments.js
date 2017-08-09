

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
    if (mode == 'A') {
       modeCreation("Mode: Admin");
    }
}

function resetButtons(containerId)
{
    var c = document.getElementById(containerId);
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

function hideColDiv(containerId)
{
    var c = document.getElementById(containerId);
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

function enableButtons(container, enable=true)
{
    var elems = container.getElementsByClassName('btn');
    var i;
    if (enable)
    {

      for (i = 0; i < elems.length; i++) {
        $(elems[i]).removeClass('disabled');
        //alert(enable);
      }
    }
    else
    {
      //alert(enable);
      for (i = 0; i < elems.length; i++) {
        $(elems[i]).addClass('disabled');
      }
    }
}

function enableButton(button_name, enable=true)
{
    var elem = document.getElementById(button_name);
    if (enable)
    {
         $(elem).removeClass('disabled');
    }
    else
    {
        $(elem).addClass('disabled');
    }
}

function newresetButtons(container)
{
    var elems = container.getElementsByClassName('btn-success');
    var i;
    for (i = 0; i < elems.length; i++) {
      $(elems[i]).removeClass('btn-success');
    }
}

function resetButton(button)
{
  $(button).removeClass('btn-success');
}

//use this to replace selectButton
function newSelectButton(button)
{
  container = button.parentNode;
  if (container) {
    newresetButtons(container);
    $(button).addClass('btn-success');
  }
}

function selectedButton(button)
{
  if ($(button).attr('class') != 'btn btn-primary')  {
      selected = true;
  }
  else {
      selected = false;
  }
  return selected
}


function selectMultiButton(item)
{
  if ($(item).attr('class') == 'btn btn-primary')  {
      $(item).addClass('btn-success');
      selected = true;
  }
  else { $(item).removeClass('btn-success');
      selected = false;
  }
  return selected
}

// use this to replace hideColDiv
function hideClassUnder(container, cl)
{
    var elems = container.getElementsByClassName(cl);
    var i;
    for (i = 0; i < elems.length; i++) {
      $(elems[i]).hide();
    }
}

function activateTargetDiv(targetId, cl='col-md-20')
{
  if (targetId)
  {
    var target = document.getElementById(targetId);
    container = target.parentNode;
    hideClassUnder(container, cl);
    $(target).show();
  }
}

function setAttr(elemId,attr,value) {
   var elem = document.getElementById(elemId);
   if (elem) { elem.setAttribute(attr,value);}
}

function selectListItemUnique(item, grouplist_name)
{
    // check if there are selected elements in the group list
    var elems = selectedElemsInGroupList(grouplist_name);
    var i;
    for (i = 0; i < elems.length; i++) {
     // remove the selection
      $(elems[i]).removeClass('list-group-item-warning');
    }
    $(item).addClass('list-group-item-warning');
  // }
  // set the indicated element as selected
  return true
}

function selectListItemUniqueDeselect(item, grouplist_name)
{
    // check if there are selected elements in the group list
    var elems = selectedElemsInGroupList(grouplist_name);
    var i;
    var was_selected = ($(item).attr('class') != 'list-group-item');
    for (i = 0; i < elems.length; i++) {
     // remove the selection
      $(elems[i]).removeClass('list-group-item-warning');
    }
    if (!was_selected)
    {    $(item).addClass('list-group-item-warning'); }
  // }
  // set the indicated element as selected
  return true
}

function selectListItem(item)
{
  if ($(item).attr('class') == 'list-group-item') {
      $(item).addClass('list-group-item-warning');
      selected = true;
  }
  else {
      $(item).removeClass('list-group-item-warning');
      selected = false;
  }
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

function selectedElemsInDiv(item_name)
{
    var elems = [];
    var elem = document.getElementById(item_name);
    // get the list-group within that div
    var list_group = elem.getElementsByClassName('list-group');
    if (list_group.length > 0)
    {
      elem = list_group[0]; //assuming only one
      // get all the selected elements within the list group
      elems = elem.getElementsByClassName('list-group-item-warning');
    }
    return elems
}

function selectListItemUniqueWithTarget(item)
{
  var parent = findAncestor(item, "list-group");
  var selected = $(parent).attr('target');
  if (selected)
  {
    var elem = document.getElementById(selected);
    // de-selected previously selected item
    selectListItem(elem);
  }
  // select previously selected item
  selectListItem(item);
  // saving the currently selected correspondence
  parent.setAttribute("target",$(item).attr('id'));
  return true
}

function findAncestor (el, cls) {
//    console.log(el);
    while ((el = el.parentElement) && !el.classList.contains(cls));
    return el;
}

function addNote(text, cl='danger')
{
    // class = danger, info, success, warning
    var note = '<div class="'+cl+' style="scroll: both; overflow: auto; width: 5em;" text-right"><p style="color:black">' + text +'&nbsp&nbsp</p></div>';
    return note;
}

function loadingGif(sourceElem, nLevel, show=true)
{
    var elem = sourceElem;
    for (var i=0; i<nLevel; i++) {
        elem = elem.parentNode;
    }
    var loadDivs = elem.getElementsByClassName("loading");
    if (loadDivs.length > 0)
    {
        var loadDiv = loadDivs[0];
        if (show)
        {    $(loadDiv).show();
             start = new Date();
             chrono($(sourceElem).attr('id'), nLevel);
        } else
        {   $(loadDiv).hide();
            clearTimeout(timerID);

        }
    }
}

function getSelectIndexes(select) {
  var result = [];
  var options = select && select.options;
  var opt;

  for (var i=0; i<options.length; i++) {
    opt = options[i];
    if (opt.selected) {
      result.push(i);
    }
  }
//  alert(result);
  return result;
}

// Return an array of the selected opion values
// select is an HTML select element
function getSelectValues(select) {
  var result = [];
  var options = select && select.options;
  var opt;

  for (var i=0, iLen=options.length; i<iLen; i++) {
    opt = options[i];

    if (opt.selected) {
      result.push(opt.text);
    }
  }
  return result;
}

// ------------------------------------------------------------------- //
// Admin mode

function modeAdmin(val)
{
   // change the name and mode of the button modeDropdown
   var y = document.getElementById('modeDropdown');
   $(y).html(val + '<span class="caret"></span>');
   y.setAttribute("mode", 'A');

   // hide investigation div
   $('#divInvestigation').hide();
   $('#investigation_buttons_col').hide();
   $('#divCreation').hide();
   $('#creation_buttons_col').hide();

   // "empty" and show divCreation
   //hideColDiv('divCreation');
   //$('#divCreation').show();

   // reset all buttons in the admin mode to primary and show
//   resetButtons('admin_buttons_col');
   $('#admin_buttons_col').show();
}

function DelRQClick()
{
    $("#divAdmin").show();
    $("#deletion_dataset_col").show();
    $("#deletion_idea_row").show();

   $('#button_select_RQ_col').html('Loading...');
   // get research questions
   $.get('/getrquestions',
          data = {'template': 'list_dropdown.html',
                  'function': 'rqAdminClick(this,"idea")'},
          function(data)
   {
     //load the results rendered as a button into a div-col
     $('#button_select_RQ_col').html(data);
   });

  var target = 'deletion_idea_selected_RQ';
  setAttr(target,'uri','');
  setAttr(target,'label','');
  setAttr(target,'style','background-color:none');
  $('#'+target).html('');

}

function rqAdminClick(th, mode)
{
  // get the values of the selected rq
  var rq_uri = $(th).attr('uri');
  var rq_label = $(th).attr('label');

  //set target div with selected RQ
  var target = 'deletion_idea_selected_RQ';
  setAttr(target,'uri',rq_uri);
  setAttr(target,'label',rq_label);
  setAttr(target,'style','background-color:lightblue');
  $('#'+target).html(rq_label);
}

function deleteIdeaButtonClick()
{
    var rq_uri = $('#deletion_idea_selected_RQ').attr('uri');
    if (rq_uri)
    {
        $('#idea_deletion_message_col').html(addNote('Deleting the selected Research Question',cl='warning'));
        loadingGif(document.getElementById('idea_deletion_message_col'), 2);
        $.get('/adminDel',
          data = {'typeDel': 'idea', 'uri': rq_uri},
          function(data)
          {
             $('#idea_deletion_message_col').html(addNote(data,cl='info'));
             loadingGif(document.getElementById('idea_deletion_message_col'), 2, show=false);
             DelRQClick(); // Refresh
          });
    }
    else
    {   var test = confirm("Press a button!");
        if (test)
        {   $('#idea_deletion_message_col').html(addNote('Deleting ALL Research Questions',cl='warning'));
            loadingGif(document.getElementById('idea_deletion_message_col'), 2);
            $.get('/adminDel',
              data = {'typeDel': 'idea'},
              function(data)
              {
                 $('#idea_deletion_message_col').html(addNote(data,cl='info'));
                 loadingGif(document.getElementById('idea_deletion_message_col'), 2, show=false);
                 DelRQClick(); // Refresh
              });
        }

    }
}

function del_ideas_button()
{
//    alert("in");
    var test = confirm("Delete all the research questions?");
    if (test)
    {
        $.get('/adminDel',
              data = {'typeDel': 'idea'},
              function(data)
       {
        alert("done");
       });
        //alert("out");
    }
}


function del_linksets_button()
{
    var test = confirm("Delete all the linksets?");
    if (test)
    {
       $.get('/adminDel',
              data = {'typeDel': 'linkset'},
              function(data)
       {
        alert("done");
       });
    }
}

function del_lenses_button()
{
    var test = confirm("Delete all the lenses?");
    if (test)
    {
       $.get('/adminDel',
              data = {'typeDel': 'lens'},
              function(data)
       {
        alert("done");
       });
    }
}

function filterListGroup(input,div_id) {
    // Declare variables
    // var input,
     var filter, ul, li, a, i;
    //input = document.getElementById('myInput');
    filter = input.value.toUpperCase();
    ul = document.getElementById(div_id);
    li = ul.getElementsByTagName('li');

    // Loop through all list items, and hide those who don't match the search query
    for (i = 0; i < li.length; i++) {
        //a = li[i].getElementsByTagName("a")[0];
        if (li[i].innerHTML.toUpperCase().indexOf(filter) > -1) {
            li[i].style.display = "";
        } else {
            li[i].style.display = "none";
        }
    }
}

///////////////////////////////////
// Download html table to csv
////////////////////////////////////

function exportTableToCSV($table, filename) {

    var $rows = $table.find('tr:has(td),tr:has(th)'),

        // Temporary delimiter characters unlikely to be typed by keyboard
        // This is to avoid accidentally splitting the actual contents
        tmpColDelim = String.fromCharCode(11), // vertical tab character
        tmpRowDelim = String.fromCharCode(0), // null character

        // actual delimiter characters for CSV format
        colDelim = '","',
        rowDelim = '"\r\n"',

        // Grab text from table into CSV formatted string
        csv = '"' + $rows.map(function (i, row) {
            var $row = $(row), $cols = $row.find('td,th');

            return $cols.map(function (j, col) {
                var $col = $(col), text = $col.text();

                return text.replace(/"/g, '""'); // escape double quotes

            }).get().join(tmpColDelim);

        }).get().join(tmpRowDelim)
            .split(tmpRowDelim).join(rowDelim)
            .split(tmpColDelim).join(colDelim) + '"',



        // Data URI
        csvData = 'data:application/csv;charset=utf-8,' + encodeURIComponent(csv);

//        console.log(csvData);

        if (window.navigator.msSaveBlob) { // IE 10+
            //alert('IE' + csv);
            window.navigator.msSaveOrOpenBlob(new Blob([csv], {type: "text/plain;charset=utf-8;"}), "csvname.csv")
        }
        else {
//            alert('chrom' + csvData);
            $(this).attr({ 'download': filename, 'href': csvData, 'target': '_blank' });
            console.log(this);
        }
}

// This must be a hyperlink
$("#downloadResultTable").on('click', function (event) {

    exportTableToCSV.apply(this, [$('#resultTable'), 'export.csv']);

    // IF CSV, don't do event.preventDefault() or return false
    // We actually need this to be a typical hyperlink
});

function exportResultToCSV($query, filename) {

//    $('#downloadResultTable').html('<button type="button" class="btn btn-primary"> Download Table <span class="badge alert-info chronotime">0:00:00:00</span> </button> ');
    loadingGif(document.getElementById('view_download_message_col'), 2);
    $('#view_download_message_col').html(addNote('Loading...',cl='warning'));

    var query = $query.val();

    $.get('/sparqlToCSV',
          data = {'query': query},
          function(data)
    {
        var obj = JSON.parse(data);
        loadingGif(document.getElementById('view_download_message_col'), 2, show=false);

        if (obj.message == 'OK')
        {
            message = 'Have a look at the downloaded file';
            $('#view_download_message_col').html(addNote(message,cl='info'));
            csv = obj.result;

            // Data URI
            csvData = 'data:application/csv;charset=utf-8,' + encodeURIComponent(csv);

//            console.log(csvData);

            if (window.navigator.msSaveBlob) { // IE 10+
                alert('IE' + csv);
                window.navigator.msSaveOrOpenBlob(new Blob([csv], {type: "text/plain;charset=utf-8;"}), "csvname.csv")
            }
            else {
//                alert('chrom' + csvData);
                $(this).attr({ 'download': filename, 'href': csvData, 'target': '_blank' });
                console.log(this);
            }
        }
        else
        {
            $('#view_download_message_col').html(addNote(obj.message));
        }

    });
}

// This must be a hyperlink
$("#downloadResultQuery").on('click', function (event) {

    exportResultToCSV.apply(this, [$('#queryView'), 'export.csv']);

    // IF CSV, don't do event.preventDefault() or return false
    // We actually need this to be a typical hyperlink
});


function download(th, filename, query) {

//    $(th).html('Download Table <span class="badge alert-info chronotime">0:00:00:00</span>');
    loadingGif(document.getElementById('view_download_message_col'), 2);
    $('#view_download_message_col').html(addNote('Loading...',cl='warning'));

    $.get('/sparqlToCSV',
          data = {'query': query},
          function(data)
    {
        var obj = JSON.parse(data);
        loadingGif(document.getElementById('view_download_message_col'), 2, show=false);

        if (obj.message == 'OK')
        {
            message = 'Have a look at the downloaded file';
            $('#view_download_message_col').html(addNote(message,cl='info'));
            csv = obj.result;

            var element = document.createElement('a');
            element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(csv));
            element.setAttribute('download', filename);

            element.style.display = 'none';
            document.body.appendChild(element);

            element.click();

            document.body.removeChild(element);

        }
        else
        {
            $('#view_download_message_col').html(addNote(obj.message));
        }

    });
}

var startTime = 0
var start = 0
var end = 0
var diff = 0
var timerID = 0
function chrono(elemID, nLevel){
	end = new Date()
	diff = end - start
	diff = new Date(diff)
	var msec = diff.getMilliseconds()
	var sec = diff.getSeconds()
	var min = diff.getMinutes()
	var hr = diff.getHours()-1
	if (min < 10){
		min = "0" + min
	}
	if (sec < 10){
		sec = "0" + sec
	}
	if(msec < 10){
		msec = "00" +msec
	}
	else if(msec < 100){
		msec = "0" +msec
	}

    var elem = document.getElementById(elemID);
    for (var i=0; i<nLevel; i++) {
        elem = elem.parentNode;
    }

    var chronos = elem.getElementsByClassName("chronotime");
    if (chronos.length > 0)
    {
        chrono_elem = chronos[0];
        $(chrono_elem).show();
        chrono_elem.innerHTML = hr + ":" + min + ":" + sec + ":" + msec
        timerID = setTimeout('chrono("'+elemID+'", '+nLevel+')', 10)
    }
}

function chronoReset(){
	$('.chronotime').hide();
}


