//$.get('/print',function(){});

$( document ).ready(function()
{
    $('#corresponsence_list_row').hide();

    $('#menu_list_col a').on('click',function()
    {
        document.getElementById("modeDropdown").innerText;
        document.getElementById("modeDropdown").text="Close Curtain";
//        var data = {'test': 'test'}
//        $('#modeDropdown').html(data);
    });

    // CALL THE GRAPHS FUNCTION FOR LOADING GRAPHS INTO RESPECTIVE BUTTONS
    $.get('/getgraphs',function(data)
    {
        $('#corresponsence_list_row').hide();
        $('#graphs_list_col').html(data);

        $('#startButton').on('click',function()
        {
            $('#corresponsence_list_row').hide();
            window.location.reload(false);
        });

        // ON CLICK BUTTON FOR DISPLAYING THE LIST OF CORRESPONDENCES
        $('#graphs_list_col a').on('click',function()
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
                            $('#corresp2_list_col').html(data);

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
                            $('#corresp2_list_col').html(data);

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

                    // $('#linktarget5').html(message);

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

                    })

                })

            })
        })
    });


});
