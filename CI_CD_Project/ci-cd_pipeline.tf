
resource "aws_s3_bucket" "new_codepipeline_bucket" {
  bucket = "new-codepipeline-bucket-us-east-1"
  acl    = "private"

  tags = {
    Name        = "NewCodePipelineBucket"
    Environment = "Dev"
  }
}
resource "aws_codepipeline" "Newpipe" {
  name     = "Newpipe"
  role_arn = "arn:aws:iam::975050352921:role/service-role/AWSCodePipelineServiceRole-us-east-1-Newpipe"

  artifact_store {
    type     = "S3"
    location = aws_s3_bucket.new_codepipeline_bucket.bucket
  }

  stage {
    name = "Source"

    action {
      name             = "Source"
      category         = "Source"
      owner            = "ThirdParty"
      provider         = "GitHub"
      version          = "1"
      output_artifacts = ["source_output"]
      configuration = {
        Owner      = "JaideepSingh2"
        Repo       = "testingcicd"
        Branch     = "main"
        OAuthToken = ""
        PollForSourceChanges = true
      }
      
    }
  }

  stage {
    name = "Deploy"

    action {
      name             = "Deploy"
      category         = "Deploy"
      owner            = "AWS"
      provider         = "ElasticBeanstalk"
      input_artifacts  = ["source_output"]
      configuration = {
        ApplicationName = "AGMS1"
        EnvironmentName = "AGMS1-env"
      }
      version = "1"
      run_order = 1
    }
  }
}