

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
      // alert(enable);
      for (i = 0; i < elems.length; i++) {
        $(elems[i]).removeClass('disabled');
      }
    }
    else
    {
      // alert(enable);
      for (i = 0; i < elems.length; i++) {
        $(elems[i]).addClass('disabled');
      }
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
    while ((el = el.parentElement) && !el.classList.contains(cls));
    return el;
}
