import csv
import os
from django.apps import apps
from django.core.management.base import BaseCommand, CommandError
from reviews.models import User


class Command(BaseCommand):

    def insert_users_to_db(self, data):
        try:
            User.objects.create(
                username=data['username'],
                email=data['email'],
                role=data["role"],
                bio=data['bio'],
                first_name=data['first_name'],
                last_name=data['last_name'],
            )
        except Exception as e:
            raise CommandError("Error in inserting {}: {}".format(
                User, str(e)))

    

    def get_current_app_path(self):
        return apps.get_app_config('reviews').path

    def get_csv_file(self, filename):
        app_path = self.get_current_app_path()
        file_path = os.path.join(app_path, "management",
                                 "commands", filename)
        return file_path

    def add_arguments(self, parser):
        parser.add_argument('filenames',
                            nargs='+',
                            type=str,)

    def handle(self, *args, **options):

        for filename in options['filenames']:
            self.stdout.write(
                self.style.SUCCESS('Reading:{}'.format(filename)))
            file_path = self.get_csv_file(filename)
            try:
                with open(file_path) as csv_file:
                    csv_reader = csv.reader(csv_file, delimiter=',')
                    for row in csv_reader:
                        username = row[1]
                        email = row[2]
                        role = row[3]
                        bio = row[4]
                        first_name = row[5]
                        last_name = row[6]
                        data = {}
                        data['username'] = username
                        data['email'] = email
                        data["role"] = role
                        data['bio'] = bio
                        data['first_name'] = first_name
                        data['last_name'] = last_name
                        data['id'] = id
                        self.insert_users_to_db(data)
                        self.stdout.write(
                            self.style.SUCCESS('{}_{}: {}'.format(
                                username, email, role, bio, first_name, last_name,
                            )
                            )
                        )

            except FileNotFoundError:
                raise CommandError("File {} does not exist".format(
                    file_path))
