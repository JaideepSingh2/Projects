
resource "aws_lambda_function" "stop_ec2" {
  function_name = "stop_ec2"
  runtime       = "python3.12"
  role          = "arn:aws:iam::975050352921:role/Stop-ec2-instance"
  handler       = "lambda_function.lambda_handler"

  filename      = "C:/Terraformcodes/Lamdacode/lambda/start/lambda_function.zip"
  source_code_hash = filebase64sha256("lambda_function_python_code.zip")

  environment {
    variables = {
      
    }
  }
}

resource "aws_iam_role_policy_attachment" "lambda_policy_attachment" {
  role       = "Stop-ec2-instance"
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}