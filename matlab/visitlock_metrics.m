function visitlock_metrics(csvPath, outDir)
%VISITLOCK_METRICS  Quote confirmation_rate and no_show_risk from fixture outcomes CSV.
% Not a Simulink .slx door — CSV in, quoted numbers out for the HUD board JSON.
if nargin < 1 || isempty(csvPath)
    error('csvPath required');
end
if nargin < 2 || isempty(outDir)
    outDir = pwd;
end
if ~exist(outDir, 'dir')
    mkdir(outDir);
end

T = readtable(csvPath, 'TextType', 'string');
status = lower(string(T.visit_status));
called = numel(status);
confirmed = sum(status == "yes");
reschedule_count = sum(status == "reschedule");
no_answer = sum(status == "no_answer");
declined = sum(status == "no");

if called == 0
    confirmation_rate = 0;
else
    confirmation_rate = 100 * confirmed / called;
end

% Simple no-show risk score: weight non-yes outcomes (0-100).
% no_answer high risk, no medium, reschedule moderate, unknown low-medium.
risk = 0;
risk = risk + 35 * no_answer;
risk = risk + 25 * declined;
risk = risk + 15 * reschedule_count;
risk = risk + 10 * sum(status == "unknown");
if called > 0
    no_show_risk = min(100, risk / called);
else
    no_show_risk = 0;
end

fid = fopen(fullfile(outDir, 'metrics.json'), 'w');
fprintf(fid, '{\n');
fprintf(fid, '  "called": %d,\n', called);
fprintf(fid, '  "confirmed": %d,\n', confirmed);
fprintf(fid, '  "reschedule_count": %d,\n', reschedule_count);
fprintf(fid, '  "confirmation_rate": %.1f,\n', confirmation_rate);
fprintf(fid, '  "no_show_risk": %.1f,\n', no_show_risk);
fprintf(fid, '  "source": "matlab_visitlock_metrics",\n');
fprintf(fid, '  "engine": "MATLAB R2025b"\n');
fprintf(fid, '}\n');
fclose(fid);

fid = fopen(fullfile(outDir, 'quoted_numbers.txt'), 'w');
fprintf(fid, 'confirmation_rate=%.1f\n', confirmation_rate);
fprintf(fid, 'no_show_risk=%.1f\n', no_show_risk);
fprintf(fid, 'confirmed=%d\n', confirmed);
fprintf(fid, 'called=%d\n', called);
fprintf(fid, 'reschedule_count=%d\n', reschedule_count);
fclose(fid);

fprintf('VisitLock MATLAB metrics: confirmation_rate=%.1f no_show_risk=%.1f (%d/%d)\n', ...
    confirmation_rate, no_show_risk, confirmed, called);
end
