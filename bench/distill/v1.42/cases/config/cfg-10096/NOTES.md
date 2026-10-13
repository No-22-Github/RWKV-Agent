## Traps
- TR-READONLY: k8s/jobs/* keep 1 replica and 256Mi per k8s/README.md.
- 4 files change; 3 stay byte-identical.

## Reference solution
1. bash: `find k8s -name deploy.yaml -not -path '*/jobs/*' | xargs sed -i 's/^  replicas: 1$/  replicas: 2/'`
2. bash: `find k8s -name deploy.yaml -not -path '*/jobs/*' | xargs sed -i 's/^              memory: 256Mi$/              memory: 512Mi/'`
3. bash: `grep -rn -e replicas -e memory k8s`
Final answer: The four service deployments now run 2 replicas with 512Mi limits; the jobs folder is unchanged. Verified with grep. DONE

## Why the answer is unique
The end state is fixed line by line by the request and the protected range; expect.files pins every changed file and the untouched ones.
