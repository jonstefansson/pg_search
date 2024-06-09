# GitHub Copilot generated this code for me. It is an ActiveRecord
# migration that creates a trigger to keep a tsvector column up to date.
class AddTriggerToUpdateTsvectorColumn < ActiveRecord::Migration[6.0]
  def up
    execute <<-SQL
      CREATE OR REPLACE FUNCTION update_searchable_full_name() RETURNS TRIGGER AS $$
      BEGIN
        NEW.searchable_full_name := to_tsvector('english', NEW.name_last || ', ' || NEW.name_first);
        RETURN NEW;
      END
      $$ LANGUAGE plpgsql;

      CREATE TRIGGER update_searchable_full_name_trigger
      BEFORE INSERT OR UPDATE ON authors
      FOR EACH ROW EXECUTE FUNCTION update_searchable_full_name();
    SQL
  end

  def down
    execute <<-SQL
      DROP TRIGGER update_searchable_full_name_trigger ON authors;
      DROP FUNCTION update_searchable_full_name;
    SQL
  end
end
