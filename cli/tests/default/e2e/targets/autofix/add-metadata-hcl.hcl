resource "aws_instance" "example1" {
  ami           = "ami-005e54dee72cc1d01"
  instance_type = "t2.micro"
}

resource "aws_instance" "example2" {
  ami           = "ami-005e54dee72cc1d02"
  instance_type = "t2.micro"
}
