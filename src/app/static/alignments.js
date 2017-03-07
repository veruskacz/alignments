$( document ).ready(function()
{
    $('#gl_list_row').hide();
    $('#rec_list_row').hide();


    $('#startButton').on('click',function()
    {
        $.get('/getgraphs',function(data)
        {
            $('#gl_list_row').hide();
            $('#rec_list_row').hide();
            $('#gl_list_col').html(data);

            $('#gl_list_col a').on('click',function()
            {
                var uri = $(this).attr('uri');
                var label = $(this).attr('label');

                $('#rec_list_col').html('Loading...');
                $('#rec_list_row').show();

                $.get('/getcorrespondences',data={'uri': uri, 'label': label},function(data)
                {

                    $('#rec_list_col').html(data);

                    // $("#rec_list_col span").on('mouseover',function()
                    // {
                    //     var uri = $(this).attr('target');
                    //
                    //     $("a[uri=\""+uri+"\"]").addClass('list-group-item-warning');
                    // });

                    // $("#rec_list_col span").on('mouseout',function()
                    // {
                    //     var uri = $(this).attr('target');
                    //
                    //     $("a[uri=\""+uri+"\"]").removeClass('list-group-item-warning');
                    // });

                    $("#rec_list_col a").on('click', function()
                    {
                        var uri = $(this).attr('uri');
                        var sub_uri = $(this).attr('sub_uri');
                        var obj_uri = $(this).attr('obj_uri');
                        var subjectTarget = $(this).attr('subjectTarget');
                        var objectTarget = $(this).attr('objectTarget');
                        var subjectTarget_uri = $(this).attr('subjectTarget_uri');
                        var objectTarget_uri = $(this).attr('objectTarget_uri');

                        var data = data={'uri': uri, 'sub_uri': sub_uri, 'obj_uri': obj_uri,
                                          'subjectTarget': subjectTarget,
                                          'objectTarget': objectTarget}
                        $.get('/getdetails',data=data,function(data)
                        {
                          $('#corresp2_list_col').html(data);

                          $("#srcDataset").on('click', function()
                          {
                              $.get('/getdatadetails',data={'dataset_uri': subjectTarget_uri, 'resource_uri': sub_uri},function(data)
                              {
                                $('#srcDetails').html(data);
                              });
                          });

                          $("#trgDataset").on('click', function()
                          {
                              $.get('/getdatadetails',data={'dataset_uri': objectTarget_uri, 'resource_uri': obj_uri},function(data)
                              {
                                $('#trgDetails').html(data);
                              });
                          });

                        });

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

            $('#gl_list_row').show();
        });
    });

});
