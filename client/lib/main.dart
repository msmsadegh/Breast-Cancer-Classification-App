import 'dart:io';
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

void main() {
  runApp(MyApp());
}

class MyApp extends StatefulWidget {
  @override
  _MyAppState createState() => _MyAppState();
}

class _MyAppState extends State<MyApp> {
  File? _image;
  final picker = ImagePicker();
  String _prediction = "";
  String? _gradcamImage;

  Future pickImage() async {
    final pickedFile = await picker.pickImage(source: ImageSource.gallery);

    if (pickedFile != null) {
      setState(() {
        _image = File(pickedFile.path);
        _gradcamImage = null;
      });
      sendImageToServer(_image!);
    }
  }

  Future sendImageToServer(File imageFile) async {
    var request = http.MultipartRequest(
        'POST', Uri.parse('http://127.0.0.1:8000/predict/'));
    request.files
        .add(await http.MultipartFile.fromPath('file', imageFile.path));

    var response = await request.send();
    if (response.statusCode == 200) {
      var responseData = await response.stream.bytesToString();
      var jsonResponse = json.decode(responseData);
      setState(() {
        _prediction =
            "کلاس پیش بینی شده: ${jsonResponse['predicted_class']}\nConfidence: ${jsonResponse['confidence_scores']}";
        _gradcamImage = jsonResponse['gradcam_image'];
      });
    } else {
      setState(() {
        _prediction = "Error in prediction";
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      home: Scaffold(
        appBar: AppBar(title: Text('Image Classifier')),
        body: Center(
          child: SingleChildScrollView(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                _image == null
                    ? Text('No image selected')
                    : Image.file(_image!, height: 200),
                SizedBox(height: 20),
                ElevatedButton(
                  onPressed: pickImage,
                  child: Text('Pick Image'),
                ),
                SizedBox(height: 20),
                Text('کلاس خوش خیم برابر 0 و کلاس بدخیم برابر 1 قرار میگیرید.'),
                SizedBox(height: 20),
                Text(_prediction, textAlign: TextAlign.center),
                SizedBox(height: 20),
                _gradcamImage != null
                    ? Image.memory(base64Decode(_gradcamImage!))
                    : Container(),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
