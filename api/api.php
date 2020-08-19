<?php

header('Content-Type: application/json');

define('LANG', isset($_GET['et']) ? 'et' : 'en');

$file = LANG === 'et' ? 'main_cats_et.json' : 'main_cats.json';

$data = file_get_contents('./../data/' . $file);

echo $data;