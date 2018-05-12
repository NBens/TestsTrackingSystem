CREATE TABLE "test_owners" (
	"id" serial NOT NULL,
	"username" VARCHAR(255) NOT NULL,
	"password" VARCHAR(255) NOT NULL,
	"salt" VARCHAR(255) NOT NULL,
	"added_by_admin_id" integer NOT NULL,
	CONSTRAINT test_owners_pk PRIMARY KEY ("id")
) WITH (
  OIDS=FALSE
);



CREATE TABLE "testing_environment" (
	"id" serial NOT NULL,
	"test_owner_id" integer NOT NULL,
	"name" VARCHAR(255) NOT NULL,
	"platform" VARCHAR(255) NOT NULL,
	"version" VARCHAR(255) NOT NULL DEFAULT 'NULL',
	"description" TEXT NOT NULL,
	CONSTRAINT testing_environment_pk PRIMARY KEY ("id")
) WITH (
  OIDS=FALSE
);



CREATE TABLE "tests" (
	"id" serial NOT NULL,
	"cwd" VARCHAR(255) NOT NULL,
	"root" VARCHAR(255) NOT NULL,
	"testing_environment_id" integer NOT NULL,
	"test_cases" integer NOT NULL,
	"test_programs" integer NOT NULL,
	"upload_date" VARCHAR(255) NOT NULL,
	"test_date" VARCHAR(255) NOT NULL,
	"sysname" VARCHAR(255) NOT NULL,
	"release" VARCHAR(255) NOT NULL,
	"port" VARCHAR(255) NOT NULL,
	CONSTRAINT tests_pk PRIMARY KEY ("id")
) WITH (
  OIDS=FALSE
);



CREATE TABLE "test_programs" (
	"id" serial NOT NULL,
	"test_id" integer NOT NULL,
	"absolute_path" VARCHAR(255) NOT NULL,
	"root" VARCHAR(255) NOT NULL,
	"relative_path" VARCHAR(255) NOT NULL,
	"test_suite_name" VARCHAR(255) NOT NULL,
	"tp_time" FLOAT NOT NULL,
	CONSTRAINT test_programs_pk PRIMARY KEY ("id")
) WITH (
  OIDS=FALSE
);



CREATE TABLE "test_cases" (
	"id" serial NOT NULL,
	"test_program_id" integer NOT NULL,
	"result" VARCHAR(255) NOT NULL,
	"result_reason" TEXT NOT NULL,
	"name" VARCHAR(255) NOT NULL,
	"tc_time" FLOAT NOT NULL,
	CONSTRAINT test_cases_pk PRIMARY KEY ("id")
) WITH (
  OIDS=FALSE
);



CREATE TABLE "files" (
	"id" serial NOT NULL,
	"test_case_id" integer NOT NULL,
	"file_type" VARCHAR(255) NOT NULL,
	"content" TEXT NOT NULL,
	CONSTRAINT files_pk PRIMARY KEY ("id")
) WITH (
  OIDS=FALSE
);



CREATE TABLE "env_variables" (
	"id" serial NOT NULL,
	"name" VARCHAR(255) NOT NULL,
	"value" VARCHAR(255) NOT NULL,
	"test_id" integer NOT NULL,
	CONSTRAINT env_variables_pk PRIMARY KEY ("id")
) WITH (
  OIDS=FALSE
);



CREATE TABLE "admins" (
	"id" serial NOT NULL,
	"username" VARCHAR(255) NOT NULL,
	"password" VARCHAR(255) NOT NULL,
	"email" VARCHAR(255) NOT NULL,
	"salt" VARCHAR(255) NOT NULL,
	CONSTRAINT admins_pk PRIMARY KEY ("id")
) WITH (
  OIDS=FALSE
);



ALTER TABLE "test_owners" ADD CONSTRAINT "test_owners_fk0" FOREIGN KEY ("added_by_admin_id") REFERENCES "admins"("id");

ALTER TABLE "testing_environment" ADD CONSTRAINT "testing_environment_fk0" FOREIGN KEY ("test_owner_id") REFERENCES "test_owners"("id");

ALTER TABLE "tests" ADD CONSTRAINT "tests_fk0" FOREIGN KEY ("testing_environment_id") REFERENCES "testing_environment"("id");

ALTER TABLE "test_programs" ADD CONSTRAINT "test_programs_fk0" FOREIGN KEY ("test_id") REFERENCES "tests"("id");

ALTER TABLE "test_cases" ADD CONSTRAINT "test_cases_fk0" FOREIGN KEY ("test_program_id") REFERENCES "test_programs"("id");

ALTER TABLE "files" ADD CONSTRAINT "files_fk0" FOREIGN KEY ("test_case_id") REFERENCES "test_cases"("id");

ALTER TABLE "env_variables" ADD CONSTRAINT "env_variables_fk0" FOREIGN KEY ("test_id") REFERENCES "tests"("id");


