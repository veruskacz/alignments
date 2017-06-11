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
        { type = 'dataset'
        }
        else
        { type = 'linkset' }

        $.get('/getupload',
              data={'type':  type, 'original': response.original},
              function(data)
        {
//            var obj = JSON.parse(data);
            $.data(file).addClass('done');
            if (type == 'dataset')
            { $('#ds_files_list').html("<option>-- Select a file to view a sample --</option>"+data.selectlist);  }
            else
            { $('#ds_files_list').html("<option>-- Select a predicate --</option>"+data.selectlist); }

            setAttr('viewAlignmentButton','file_path',data.original)
        });

		},

    	error: function(err, file) {
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
            else
            {  var extensions = new Array("csv", "tsv", "txt"); }
            ext = file.name.slice((file.name.lastIndexOf(".") - 1 >>> 0) + 2);
//            alert(file.name);

            if (extensions.lastIndexOf(ext) != -1)
            {

            }
            else
            {
                alert('File type not allowed!');
//                alert('Only tabular files such as: (.csv .tsv .txt) are allowed!');
                return false;
            }

        },

		uploadStarted: function(i, file, len){
			createImage(file);
		},

		progressUpdated: function(i, file, progress) {
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
	}

});
