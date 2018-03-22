$(function(){

	var dropbox = $('#dropbox'),
		message = $('.message', dropbox);


	dropbox.filedrop({
	    type: 'POST',
		paramname: 'file',
		maxfiles: 5,
    	maxfilesize: 50000,
		url: '/upload',
		uploadFinished:function(i,file,response){
		refresh_import(mode='upload');

        if (selectedButton(document.getElementById('btn_import_dataset')))
        { type = 'dataset' }
        else if (selectedButton(document.getElementById('btn_import_alignment')))
        { type = 'linkset' }
        else
        { type = 'rquestion' }

//        alert("reponse original:"+response.original);

        $.get('/getupload',
              data={'type':  type, 'original': response.original},
              function(data)
        {
//            alert("get upload ran");
//            var obj = JSON.parse(data);
            $.data(file).addClass('done');
            console.log(data);
            if (type == 'dataset')
            { $('#ds_files_list').html("<option>-- Select a file to view a sample --</option>"+data.selectlist);  }
            else if (type == 'linkset')
            { $('#ds_files_list').html("<option>-- Select a predicate --</option>"+data.selectlist);
               setAttr('viewAlignmentButton','file_path',data.original)
            }
            else
            { $('#ds_files_list').html("<option>-- Select a file to view a summary --</option>"+data.selectlist);
              setAttr('viewRQuestionButton','file_path',data.original)
            }

//            setAttr('viewAlignmentButton','file_path',data.original)

        });

		},

    	error: function(err, file) {
//    	    alert("ERROR");
			switch(err) {
				case 'BrowserNotSupported':
					showMessage('Your browser does not support HTML5 file uploads!');
					break;
				case 'TooManyFiles':
					alert('Too many files! Please select ' + this.maxfiles + ' at most!');
					break;
				case 'FileTooLarge':
					alert(file.name + ' is too large! The size is limited to ' + this.maxfilesize + 'MB.');
					break;
				default:
					break;
			}
		},

//		beforeEach: function(file)
//		{
//			if(!file.type.match(/^.csv\//))
//			{
//				alert('Only images are allowed!');
//                return true;
//			}
//		},

//        beforeEach: function(file)
//		{
//            if(!file.type.match('.csv')){
//                alert('Only comma separated files are allowed!');
//                return false;
//            }
//        },

        beforeEach: function(file)
        {
//            console.log(file);
            if (selectedButton( document.getElementById('btn_import_alignment')))
            {  var extensions = new Array("ttl", "trig"); }
            else if (selectedButton(document.getElementById('btn_import_dataset')))
            {  var extensions = new Array("csv", "tsv", "txt"); }
            else
            {  var extensions = new Array("zip", "trig"); }

            ext = file.name.slice((file.name.lastIndexOf(".") - 1 >>> 0) + 2);
//            alert(file.name);

            if (extensions.lastIndexOf(ext) != -1)
            {
//                alert("File type allowed");
            }
            else
            {
                alert('File type not allowed!');
//                alert('Only tabular files such as: (.csv .tsv .txt) are allowed!');
                return false;
            }

        },

		uploadStarted: function(i, file, len){
//		    alert("uploadStarted");
			createImage(file);
		},

		progressUpdated: function(i, file, progress) {
//		    alert("progressUpdated");
			$.data(file).find('.progress').width(progress);
		}

	});

	var template = '<div class="preview">'+
						'<span class="imageHolder">'+
							'<img />'+
							'<span class="uploaded"></span>'+
						'</span>'+
						'<div class="progressHolder">'+
							'<div class="progress"></div>'+
						'</div>'+
					'</div>';


	function createImage(file){

//        alert("createImage");
		var preview = $(template),
			image = $('img', preview);

		var reader = new FileReader();

        image.width = 100;
		image.height = 100;

		reader.onload = function(e){
			image.attr('src',e.target.result);
		};

		reader.readAsDataURL(file);

		message.hide();
		preview.appendTo(dropbox);

		$.data(file,preview);
	}

	function showMessage(msg){
		message.html(msg);
//		alert("showMessage");
	}

});
