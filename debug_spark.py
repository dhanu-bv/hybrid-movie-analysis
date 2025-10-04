import sys
import os
import traceback
import subprocess

print('Python:', sys.version.replace('\n',' '))
print('Executable:', sys.executable)
print('CWD:', os.getcwd())
print('JAVA_HOME:', os.environ.get('JAVA_HOME'))
print('PATH contains java:', any('java' in p.lower() for p in os.environ.get('PATH','').split(os.pathsep)))
try:
    print('\nRunning `java -version`...')
    jv = subprocess.run(['java','-version'], capture_output=True, text=True)
    # java prints version to stderr
    print('java -version stdout:')
    print(jv.stdout)
    print('java -version stderr:')
    print(jv.stderr)
except Exception as e:
    print('Failed to run java -version:', e)

try:
    print('\nRunning `where java`...')
    where = subprocess.run(['where','java'], capture_output=True, text=True, shell=False)
    print('where java output:')
    print(where.stdout or where.stderr)
except Exception as e:
    print('Failed to run where java:', e)

try:
    print('\nTrying to import pyspark...')
    import pyspark
    print('pyspark version:', getattr(pyspark, '__version__', 'unknown'))
    from pyspark.sql import SparkSession
    print('Attempting to create SparkSession...')
    spark = SparkSession.builder.appName('debug').master('local[1]').getOrCreate()
    print('SparkSession created:', spark)
    spark.stop()
except Exception as e:
    print('\nException occured:')
    traceback.print_exc()
    sys.exit(1)

print('\nDebug script finished successfully')
