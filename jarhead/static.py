MEDIA_BUNDLES = (
    ('mooeditable.css',
       {
            'filter': 'mediagenerator.filters.concat.Concat',
             'dev_output_name': 'mooeditable_core.css',
             'concat_dev_output': True,
             'input': (
                'css/mooeditable/Editable.css',
                'css/mooeditable/MooEditable.css',
                'css/mooeditable/MooEditable.Charmap.css',
                'css/mooeditable/MooEditable.Extras.css',
                'css/mooeditable/MooEditable.Flash.css',
                'css/mooeditable/MooEditable.Forecolor.css',
                'css/mooeditable/MooEditable.Pagebreak.css',
                'css/mooeditable/MooEditable.SilkTheme.css',
                'css/mooeditable/MooEditable.Image.css',
                'css/mooeditable/MooEditable.Smiley.css',
                'css/mooeditable/MooEditable.Table.css',
                'less/admin/image_uploader.less'         
            )
        },
    ),


    ('mooeditable.js',
        {
            'filter': 'mediagenerator.filters.concat.Concat',
             'dev_output_name': 'mooeditable_core.js',
             'concat_dev_output': True,
             'input': (
                'js/mooeditable/MooEditable.js',
                'js/mooeditable/MooEditable.Charmap.js',
                'js/mooeditable/MooEditable.CleanPaste.js',
                'js/mooeditable/MooEditable.Extras.js',
                'js/mooeditable/MooEditable.Flash.js',
                'js/mooeditable/MooEditable.Forecolor.js',
                'js/mooeditable/MooEditable.Group.js',
                'js/mooeditable/MooEditable.Image.js',
                'js/mooeditable/MooEditable.Pagebreak.js',
                'js/mooeditable/MooEditable.Smiley.js',
                'js/mooeditable/MooEditable.Table.js',
                'js/mooeditable/MooEditable.Table.js',
                'js/mooeditable/MooEditable.UI.ButtonOverlay.js',
                'js/mooeditable/MooEditable.UI.ExtendedLinksDialog.js',
                'js/mooeditable/MooEditable.UI.MenuList.js',
                "js/mooeditable/image_uploader.js",
         )},
    )




)



SUPER_ADMIN = (
   # SuperAdmin (sa) related bundles
    ('sa.css',
        'tinymce/skins/lightgray/skin.min.css',
        'less/sa/pure-min.css',
        'less/fonts.less',
        'less/fontello.less',
        'less/sa/structure.less',
    ),


    ('rich_content.css',
        'tinymce/skins/lightgray/content.min.css',
    ),

    ('less.js',
        'js/sa/less.js',
    ),

    ('sa.js',
        'tinymce/tinymce.min.js',
        'js/sa/mootools.js',
        {
            'filter': 'mediagenerator.filters.concat.Concat',
            'dev_output_name': 'file_uploader.js',
            'concat_dev_output': True,
            'input': (
                'js/FileUpload/Request.File.js',
                'js/FileUpload/Form.Upload.js',
                'js/FileUpload/Form.MultipleFileInput.js',

            )
        },
        'js/sa/libs.js',
        'js/sa/main.js',
        {'filter': 'mediagenerator.filters.media_url.MediaURL'},
    ),




)